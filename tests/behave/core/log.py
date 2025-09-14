#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from thirdparty.system import *
from thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "log_dev",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

_LOGGING_DEBUG_FILE = "tests/behave/logs/debug.log"

# ----------------------------------------------------------------
# DEBUG LOGGING FOR DEVELOPMENT
# ----------------------------------------------------------------


def log_dev(*messages: Any):
    path = _LOGGING_DEBUG_FILE
    create_file_if_not_exists(path)
    with open(path, "a") as fp:
        print(*messages, file=fp)
