#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os

from ..thirdparty.system import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "guard_directory_exists",
    "guard_file_exists",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def guard_directory_exists(
    path: str,
):
    """
    A guard which checks if file exists.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"path '{path}' does not exist!")
    if not os.path.isdir(path):
        raise FileNotFoundError(f"path '{path}' is not a directory!")
    return


def guard_file_exists(
    path: str,
):
    """
    A guard which checks if file exists.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"path '{path}' does not exist!")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"path '{path}' is not a file!")
    return
