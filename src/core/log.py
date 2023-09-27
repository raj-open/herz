#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations
from ..thirdparty.log import *
from ..thirdparty.code import *
from ..thirdparty.render import *
from ..thirdparty.types import *
from ..thirdparty.system import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'LOG_LEVELS',
    'LogProgress',
    'catch_fatal',
    'configure_logging',
    'log_debug',
    'log_dev',
    'log_error',
    'log_fatal',
    'log_info',
    'log_warn',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class LOG_LEVELS(Enum):  # pragma: no cover
    INFO = logging.INFO
    DEBUG = logging.DEBUG


# local usage only
_LOGGING_DEBUG_FILE: str = 'logs/debug.log'
T = TypeVar('T')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def configure_logging(level: str | LOG_LEVELS):
    logging.basicConfig(
        format='%(asctime)s [\x1b[1m%(levelname)s\x1b[0m] %(message)s',
        level=level.value if isinstance(level, LOG_LEVELS) else level,
        datefmt=r'%Y-%m-%d %H:%M:%S',
    )
    return


def log_debug(*messages: Any):
    logging.debug(*messages)


def log_info(*messages: Any):
    logging.info(*messages)


def log_warn(*messages: Any):
    logging.warning(*messages)


def log_error(*messages: Any):
    logging.error(*messages)


def log_fatal(*messages: Any):
    logging.fatal(*messages)
    exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Special Methods
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Intercept fatal errors
def catch_fatal(method: Callable[[], T]) -> T:
    try:
        return method()
    except Exception as e:
        log_fatal(e)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DEBUG LOGGING FOR DEVELOPMENT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def log_dev(*messages: Any):  # pragma: no cover
    path = _LOGGING_DEBUG_FILE
    p = Path(path)
    if not p.exists():
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        p.touch(mode=0o644)
    with open(_LOGGING_DEBUG_FILE, 'a') as fp:
        print(*messages, file=fp)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SPECIAL LOGGGING
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@dataclass
class LogProgress:
    name: str = field()
    steps: int = field(default=1)
    step: int = field(default=0, init=False)
    auto: bool = field(default=True)
    depth: int = field(default=0)
    tasks: int = field(default=0, init=False, repr=False)
    parent: Optional[LogProgress] = field(default=None, init=False, repr=False)
    children: list[LogProgress] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self):
        self.tasks = self.steps
        self.selfreport()
        return

    @property
    def state(self) -> str:
        dash = '-' * (3 + 2 * self.depth)
        return f'Progress {dash} \x1b[1m{self.name}\x1b[0m: {self.step}/{self.steps} ({self.step/self.steps:.2%})'

    @property
    def done(self) -> bool:
        return self.tasks <= 0

    def report(self):
        print(self.state)
        return

    def selfreport(self):
        if self.auto:
            self.report()
        return

    def subtask(self, name: str, steps: int = 1, step: int = 0, auto: Optional[bool] = None):
        self.tasks += 1
        auto = self.auto if auto is None else auto
        child = LogProgress(name=name, steps=steps, auto=auto, depth=self.depth + 1)
        child.parent = self
        self.children.append(child)
        return child

    def next(self, is_step: bool = True):
        if self.done:
            self.selfreport()
            return
        self.tasks -= 1
        if is_step:
            self.step += 1
            self.selfreport()
        if self.done and self.parent is not None:
            self.parent.next(is_step=False)
        return
