#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..generated.internal import *
from .points import *
from .conditions import *

# NOTE: foreign import
from ..generated.app import TimeInterval
from ..generated.app import PolyCritCondition
from ..generated.app import PolyDerCondition
from ..generated.app import PolyIntCondition
from ..generated.app import MarkerSettings
from ..generated.app import SpecialPointsConfig
from ..generated.app import SpecialPointsConfigs
from ..generated.app import SpecialPointsSpec

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'FittedInfo',
    'FittedInfoNormalisation',
    'MarkerSettings',
    'PolyCritCondition',
    'PolyDerCondition',
    'PolyIntCondition',
    'SpecialPointsConfig',
    'SpecialPointsConfigs',
    'SpecialPointsSpec',
    'TimeInterval',
    'get_normalisation_params',
    'get_unnormalised_data',
    'get_unnormalised_polynomial',
    'get_unnormalised_polynomial_time_only',
    'get_unnormalised_polynomial_values_only',
    'shift_conditions',
    'shift_condition',
    'shift_der_condition',
    'shift_int_condition',
]
