#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..generated.internal import *
from .poly import *
from .info import *

# NOTE: foreign import
from ..generated.app import PolyDerCondition
from ..generated.app import PolyIntCondition
from ..generated.app import MarkerSettings

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'FittedInfo',
    'FittedInfoNormalisation',
    'MarkerSettings',
    'PolyDerCondition',
    'PolyIntCondition',
    'get_normalisation_params',
    'get_rescaled_polynomial',
    'onb_conditions',
    'onb_spectrum',
]
