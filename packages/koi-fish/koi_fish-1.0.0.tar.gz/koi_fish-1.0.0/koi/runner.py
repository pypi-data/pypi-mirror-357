import itertools
import os
import subprocess
import sys
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from functools import cached_property
from itertools import chain
from threading import Event

from .logger import Logger

CONFIG_FILE = "koi.toml"


class Table:
    COMMANDS = "commands"
    DEPENDENCIES = "dependencies"
    RUN = "run"
    SUITE = "suite"


class Log:
    DELIMITER = "#########################################"
    PADDING = f"\n\t{' ' * (len(Table.COMMANDS) + 2)}"
    COLORED = "\t\033[93m{key}\033[00m"

    STATES = [
        ("\\", "|", "/", "-"),
        ("▁▁▁", "▁▁▄", "▁▄█", "▄█▄", "█▄▁", "▄▁▁"),
        ("⣾", "⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽"),
    ]


class Runner:
    def __init__(
        self,
        jobs,
        run_all,
        silent_logs,
        mute_commands,
        display_suite,
        display_all_jobs,
        described_job,
    ):
        self.cli_jobs = jobs
        self.silent_logs = silent_logs
        self.run_all = run_all
        self.mute_commands = mute_commands
        self.display_suite = display_suite
        self.display_all_jobs = display_all_jobs
        self.described_job = described_job

        self.data = {}
        self.all_jobs = []
        self.successful_jobs = []
        self.failed_jobs = []
        self.is_successful = False
        # used for spinner with --silent flag
        self.supervisor = None

    @cached_property
    def skipped_jobs(self):
        return [
            job for job in self.all_jobs if job not in chain(self.failed_jobs, self.successful_jobs)
        ]

    @cached_property
    def job_suite(self):
        if self.cli_jobs:
            self.all_jobs = self.cli_jobs
        elif self.run_all:
            self.all_jobs = (job for job in self.data if job != Table.RUN)
        elif Table.RUN in self.data:
            is_successful = self.prepare_all_jobs_from_config()
            if not is_successful:
                return None
        else:
            self.all_jobs = list(self.data)
        return {k: self.data[k] for k in self.all_jobs}

    def prepare_all_jobs_from_config(self):
        jobs = dict(self.data[Table.RUN].items())
        if Table.SUITE not in jobs:
            Logger.error(f"Error: missing key '{Table.SUITE}' in '{Table.RUN}' table")
            return False
        if not jobs[Table.SUITE]:
            Logger.error(f"Error: '{Table.RUN} {Table.SUITE}' cannot be empty")
            return False
        if not isinstance(jobs[Table.SUITE], list):
            Logger.error(f"Error: '{Table.RUN} {Table.SUITE}' must be of type list")
            return False
        if Table.RUN in jobs[Table.SUITE]:
            Logger.error(f"Error: '{Table.RUN} {Table.SUITE}' cannot contain itself recursively")
            return False
        if invalid_jobs := [job for job in jobs[Table.SUITE] if job not in self.data]:
            Logger.error(
                f"Error: '{Table.RUN} {Table.SUITE}' contains invalid jobs: {invalid_jobs}"
            )
            return False
        self.all_jobs = jobs[Table.SUITE]
        return True

    ### main flow ###
    def run(self):
        global_start = time.perf_counter()

        should_display_stats = not self.cli_jobs or len(self.cli_jobs) > 1
        should_display_job_info = self.display_suite or self.display_all_jobs or self.described_job
        if should_display_stats and not should_display_job_info:
            Logger.info("Let's go!")

        self.run_stages()
        global_stop = time.perf_counter()

        if should_display_stats:
            self.log_stats(total_time=(global_stop - global_start))

    def log_stats(self, total_time):
        if self.is_successful:
            Logger.info(f"All jobs succeeded! {self.successful_jobs}")
            Logger.info(f"Run took: {total_time}")
            return

        Logger.fail(f"Unsuccessful run took: {total_time}")
        if self.failed_jobs:
            # in case parsing fails before any job is run
            Logger.error(f"Failed jobs: {self.failed_jobs}")
        if self.successful_jobs:
            Logger.info(
                f"Successful jobs: {[x for x in self.successful_jobs if x not in self.failed_jobs]}"
            )
        if self.skipped_jobs:
            Logger.fail(f"Skipped jobs: {self.skipped_jobs}")

    def run_stages(self):
        if not (self.handle_config_file() and self.validate_cli_jobs()):
            Logger.fail("Run failed")
            sys.exit(1)
        if self.display_suite or self.display_all_jobs or self.described_job:
            self.display_jobs_info()
            sys.exit()
        self.run_jobs()

    def handle_config_file(self):
        config_path = os.path.join(os.getcwd(), CONFIG_FILE)
        if not os.path.exists(config_path):
            Logger.fail("Config file not found")
            return False
        if not os.path.getsize(config_path):
            Logger.fail("Empty config file")
            return False
        return self.read_config_file(config_path)

    def read_config_file(self, config_path):
        with open(config_path, "rb") as f:
            self.data = tomllib.load(f)
        return bool(self.data)

    def validate_cli_jobs(self):
        if not self.cli_jobs:
            return True
        if invalid_job := next((job for job in self.cli_jobs if job not in self.data), None):
            Logger.fail(f"'{invalid_job}' not found in jobs suite")
            return False
        return True

    def display_jobs_info(self):
        if self.display_suite:
            Logger.log([job for job in self.job_suite])
        elif self.display_all_jobs:
            Logger.log([job for job in self.data])
        elif self.described_job:
            for job in self.described_job:
                if not (result := self.data.get(job)):
                    Logger.fail(f"Selected job '{job}' doesn't exist in the config")
                    break
                Logger.info(f"{job.upper():}")
                Logger.log(
                    "\n".join(
                        f"{Log.COLORED.format(key=k)}: {Log.PADDING.join(v) if isinstance(v, list) else v}"
                        for k, v in result.items()
                    )
                )

    def run_jobs(self):
        if not self.job_suite:
            self.is_successful = False
            return

        is_run_successful = True
        for i, (table, table_entries) in enumerate(self.job_suite.items()):
            Logger.log(Log.DELIMITER)
            Logger.start(f"{table.upper()}:")
            start = time.perf_counter()

            install = self.build_install_command(table_entries)
            if not (run := self.build_run_command(table, table_entries)):
                return False

            cmds = self.build_commands_list(install, run)
            if not (is_job_successful := self.execute_shell_commands(cmds, i)):
                self.failed_jobs.append(table)
                Logger.error(f"{table.upper()} failed")
            else:
                stop = time.perf_counter()
                Logger.success(f"{table.upper()} succeeded! Took:  {stop - start}")
                self.successful_jobs.append(table)
            is_run_successful &= is_job_successful

        self.is_successful = is_run_successful
        Logger.log(Log.DELIMITER)

    @staticmethod
    def build_install_command(table_entries):
        if not (deps := table_entries.get(Table.DEPENDENCIES, None)):
            return None
        return deps

    def build_run_command(self, table, table_entries):
        if not (cmds := table_entries.get(Table.COMMANDS, None)):
            self.failed_jobs.append(table)
            Logger.error(f"Error: '{Table.COMMANDS}' in '{table}' table cannot be empty or missing")
            return None
        return cmds

    def build_commands_list(self, install, run):
        # NB: add more steps here e.g. teardown/cleanup after run
        cmds = []
        if install:
            if isinstance(install, list):
                cmds.extend(install)
            else:
                cmds.append(install)

        if isinstance(run, list):
            cmds.extend(run)
        else:
            cmds.append(run)
        return cmds

    def execute_shell_commands(self, cmds, i):
        if self.silent_logs:
            self.supervisor = Event()
            with ThreadPoolExecutor(2) as executor:
                with self.shell_manager(cmds):
                    executor.submit(self.spinner, i)
                    status = self.run_subprocess(cmds)
            return status
        else:
            with self.shell_manager(cmds):
                return self.run_subprocess(cmds)

    @contextmanager
    def shell_manager(self, cmds):
        try:
            if not self.mute_commands:
                Logger.info("\n".join(cmds))
            yield
        except KeyboardInterrupt:
            if self.silent_logs:
                self.supervisor.set()
            Logger.error("\033[2K\rHey, I was in the middle of something here!")
            sys.exit()
        else:
            if self.silent_logs:
                self.supervisor.set()

    def spinner(self, i):
        msg = "Keep fishin'!"
        print("\033[?25l", end="")  # hide blinking cursor
        for ch in itertools.cycle(Log.STATES[i % 3]):
            print(f"\r{ch} {msg} {ch}", end="", flush=True)
            if self.supervisor.wait(0.1):
                break
        print("\033[2K\r", end="")  # clear last line and put cursor at the begining
        print("\033[?25h", end="")  # make cursor visible

    def run_subprocess(self, cmds):
        with subprocess.Popen(
            cmds,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            executable="/bin/bash",
        ) as proc:
            if self.silent_logs:
                proc.communicate()
            else:
                # Use read1() instead of read() or Popen.communicate() as both block until EOF
                # https://docs.python.org/3/library/io.html#io.BufferedIOBase.read1
                while (text := proc.stdout.read1().decode("utf-8")) or (
                    err := proc.stderr.read1().decode("utf-8")
                ):
                    if text:
                        Logger.log(text, end="", flush=True)
                    elif err:
                        Logger.debug(err, end="", flush=True)
        return proc.returncode == 0
