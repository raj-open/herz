#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

# NOTE: many of these are part of standard python library
import os
from pathlib import Path
import pathspec
from signal import SIGINT
from signal import SIGTERM
import socket
import subprocess
import sys
import traceback
import warnings
from time import sleep

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def create_dir_if_not_exists(path: str):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return


def create_file_if_not_exists(path: str):
    create_dir_if_not_exists(os.path.dirname(path))
    p = Path(path)
    # ----------------
    # NOTE: set
    # 1. read+write access (=6) for user
    # 2. read+write access (=6) for group
    # 3. read access (=4) for others
    # ----------------
    p.touch(mode=0o664, exist_ok=True)
    return


def clear_dir_if_exists(
    path: str,
    recursive: bool = True,
):
    if not (os.path.exists(path) and os.path.isdir(path)):
        return
    for filename in os.listdir(path):
        path_ = os.path.join(path, filename)
        if os.path.isfile(path_):
            os.remove(path_)
        elif recursive:
            clear_dir_if_exists(path_, recursive=recursive)
            os.rmdir(path_)
    return


def remove_dir_if_exists(path: str):
    if not (os.path.exists(path) and os.path.isdir(path)):
        return True
    clear_dir_if_exists(path=path, recursive=True)
    os.rmdir(path)
    ex = os.path.exists(path)
    return not ex


def remove_file_if_exists(path: str) -> bool:
    if not os.path.exists(path):
        return True
    os.remove(path)
    ex = os.path.exists(path)
    return not ex


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Path',
    'SIGINT',
    'SIGTERM',
    'clear_dir_if_exists',
    'create_dir_if_not_exists',
    'create_file_if_not_exists',
    'os',
    'pathspec',
    'remove_dir_if_exists',
    'remove_file_if_exists',
    'sleep',
    'socket',
    'subprocess',
    'sys',
    'traceback',
    'warnings',
]
