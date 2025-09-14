#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import json

# for modification, not exported
from enum import Enum

import toml
import yaml
from dotenv import dotenv_values
from dotenv import load_dotenv
from pydantic_yaml import to_yaml_file
from pydantic_yaml import to_yaml_str

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def get_environment(path: str) -> dict:
    load_dotenv(dotenv_path=path)
    env = dotenv_values(path) or {}
    return env


class EnumConfigType(Enum):
    YAML = ".yaml"
    JSON = ".json"


class YamlIndentDumper(yaml.Dumper):
    """
    PyYaml's `yaml.dump` for lists yields
    ```yaml
    key:
    - value1
    - value2
    - ...
    ```
    which currently does not match standard style, i.e.
    ```yaml
    key:
      - value1
      - value2
      - ...
    ```
    This class fixes this issue.

    Usage
    ```py
    yaml.dump(..., Dumper=YamlIndentDumper)
    ```
    """

    def increase_indent(
        self,
        flow=False,
        indentless=False,
    ):
        return super(YamlIndentDumper, self).increase_indent(flow, False)


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "EnumConfigType",
    "YamlIndentDumper",
    "dotenv_values",
    "get_environment",
    "json",
    "load_dotenv",
    "to_yaml_file",
    "to_yaml_str",
    "toml",
    "yaml",
]
