#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_root_path',
    'get_source_path',
    'get_tests_path',
    'get_resources_path',
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
