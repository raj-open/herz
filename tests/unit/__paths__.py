#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
import re

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_root_path',
    'get_source_path',
    'get_tests_path',
    'get_module',
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

_root = os.path.relpath(os.path.join(os.path.dirname(__file__), '..', '..'), os.getcwd())
_source = os.path.join(_root, 'src')
_tests = os.path.relpath(os.path.dirname(__file__), os.getcwd())

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_root_path() -> str:
    return _root


def get_source_path() -> str:
    return _source


def get_tests_path() -> str:
    return _tests


def get_resources_path() -> str:
    return os.path.join(_tests, 'resources')


def get_module(path: str, root='src', prefix=r'^tests_(.*)') -> str:
    '''
    Replaces path to current file by corresponding module in source.
    '''
    path = os.path.relpath(path=path, start=_tests)
    # remove extension
    path = os.path.splitext(path)[0]
    # remove test-prefixes
    parts = re.split(pattern=r'/', string=path)
    parts = [re.sub(pattern=prefix, repl=r'\1', string=part) for part in parts]
    # join to form module name
    m = '.'.join([root] + parts)
    return m
