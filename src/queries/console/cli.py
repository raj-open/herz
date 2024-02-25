#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.io import *
from ...thirdparty.misc import *

from ...models.user import *
from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'CliArguments',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


class CliArguments(CliArgumentsBase):
    _prog = 'src/app.py'
    _part = 'APPLICATION'

    def create_parser(self) -> ArgumentParser:
        parser = self.baseparser
        parser.add_argument(
            'mode',
            choices=[e.value for e in EnumProgrammeMode],
            type=EnumProgrammeMode,  # <– DEV-NOTE: use this instead of str to force conversion
            help=dedent_full(
                f'''
                {EnumProgrammeMode.VERSION.value} = show version of programme
                {EnumProgrammeMode.REQUESTS.value} = runs processes to compute series for right-ventricular data
                '''
            ),
        )
        parser.add_argument(
            '--requests',
            type=str,
            help='Path to user requests (cases).',
            default='setup/requests.yaml',
        )
        parser.add_argument(
            '--env',
            nargs='?',
            type=str,
            help='Path to environment file.',
            default='.env',
        )
        parser.add_argument(
            '--log',
            nargs='?',
            type=str,
            help='Path to files for logging.',
            default='logs',
        )
        parser.add_argument(
            '--session',
            nargs='?',
            type=str,
            help='Path to store session information (PID).',
            default='.session',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Force logging level to be DEBUG.',
        )
        return parser
