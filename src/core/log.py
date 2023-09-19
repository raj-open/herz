#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.log import *
from ..thirdparty.render import *
from ..thirdparty.types import *
from ..thirdparty.system import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'LOG_LEVELS',
    'catch_fatal',
    'configure_logging',
    'log_debug',
    'log_dev',
    'log_error',
    'log_fatal',
    'log_info',
    'log_metrics',
    'log_progress',
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


def log_progress(name: str, index: int, n: int):
    print(f'Progress --- \x1b[1m{name}\x1b[0m: {(index + 1)/n:.2%} ({index + 1}/{n})')
    return


def log_metrics(title: str, metrics: dict[str, float], floatfmt: str = '.4g'):
    '''
    Logs a title + table of metrics.
    '''
    table = tabulate(
        tabular_data=metrics.items(),
        headers=['metric', 'value'],
        tablefmt='simple',
        floatfmt=floatfmt,
    )
    log_info(f'\x1b[1;4m{title}\x1b[0m\n{table}')
    return
