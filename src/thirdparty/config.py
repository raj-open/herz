#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import json
import yaml

import re
from typing import Any

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def yaml_key_to_js_key(key: str):
    return re.sub(r'-', repl=r'_', string=key)


def yaml_to_py_dictionary(data: Any, deep: bool = False):
    if isinstance(data, dict):
        if deep:
            return {
                yaml_key_to_js_key(key): yaml_to_py_dictionary(value, deep=True)
                for key, value in data.items()
            }
        else:
            return {yaml_key_to_js_key(key): value for key, value in data.items()}
    elif isinstance(data, list):
        return [yaml_to_py_dictionary(item, deep=deep) for item in data]
    return data


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'json',
    'yaml',
    'yaml_to_py_dictionary',
]
