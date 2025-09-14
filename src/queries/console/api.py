#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.io import *
from ...thirdparty.misc import *
from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "CliArguments",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


class CliArguments(CliArgumentsBase):
    _prog = "src/api.py"
    _part = "API"

    def create_parser(self) -> ArgumentParser:
        parser = self.baseparser
        parser.add_argument(
            "--env",
            nargs="?",
            type=str,
            help="Path to environment file.",
            default=".env",
        )
        parser.add_argument(
            "--log",
            nargs="?",
            type=str,
            help="Path to files for logging.",
            default="logs",
        )
        parser.add_argument(
            "--session",
            nargs="?",
            type=str,
            help="Path to store session information (PID).",
            default=".session",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Force logging level to be DEBUG.",
        )
        return parser
