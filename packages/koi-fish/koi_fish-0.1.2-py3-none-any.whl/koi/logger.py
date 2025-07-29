from enum import Enum


class LogLevel(Enum):
    ERROR = 91
    SUCCESS = 92
    START = 93
    FAIL = 94
    INFO = 96


class Logger:
    @classmethod
    def log(cls, msg, end="\n", flush=False):
        print(msg, end=end, flush=flush)

    @classmethod
    def error(cls, msg, end="\n", flush=False):
        cls._log(LogLevel.ERROR, msg, end=end, flush=flush)

    @classmethod
    def success(cls, msg, end="\n", flush=False):
        cls._log(LogLevel.SUCCESS, msg, end=end, flush=flush)

    @classmethod
    def start(cls, msg, end="\n", flush=False):
        cls._log(LogLevel.START, msg, end=end, flush=flush)

    @classmethod
    def fail(cls, msg, end="\n", flush=False):
        cls._log(LogLevel.FAIL, msg, end=end, flush=flush)

    @classmethod
    def info(cls, msg, end="\n", flush=False):
        cls._log(LogLevel.INFO, msg, end=end, flush=flush)

    @classmethod
    def _log(cls, level, msg, end="\n", flush=False):
        print(f"\033[{level}m{msg}\033[00m", end=end, flush=flush)
