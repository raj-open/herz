#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
from pathlib import Path
import pathspec
import signal
import socket
import sys
import traceback
import warnings

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


def temporary_folder_name(
    path: str,
    template: str = '{path}_{index}',
    create: bool = False,
):
    '''
    Ensure that a temporary folder name does not exist,
    modifying it if necessary.
    '''
    if os.path.exists(path):
        index = 1
        path_ = template.format(path=path, index=index)
        while os.path.exists(path_):
            index += 1
            path__ = path_
            path_ = template.format(path=path, index=index)
            assert path_ != path__, 'Template must generate unique names for each index!'
        path = path_
    if create and not os.path.exists(path):
        create_dir_if_not_exists(path)
    return path


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'clear_dir_if_exists',
    'create_dir_if_not_exists',
    'create_file_if_not_exists',
    'os',
    'Path',
    'pathspec',
    'remove_dir_if_exists',
    'remove_file_if_exists',
    'signal',
    'socket',
    'sys',
    'temporary_folder_name',
    'traceback',
    'warnings',
]
