#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This submodule provides the generic FilesManager interface
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from enum import Enum
from .traits import *
from .os import *

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


class EnumFilesManagementSystem(str, Enum):
    """
    Choice of location of task
    """

    OS = 'OS'


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'EnumFilesManagementSystem',
    'FilesManager',
    'FilesManagerFile',
    'FilesManagerFolder',
    'OSFilesManager',
    'OSFilesManagerFile',
    'OSFilesManagerFolder',
]
