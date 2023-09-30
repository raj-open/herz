#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..generated.internal import *
from .poly import *
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
    'get_renormalised_data',
    'get_renormalised_polynomial',
    'get_renormalised_polynomial_time_only',
    'get_renormalised_polynomial_values_only',
    'get_renormalised_coordinates_of_special_points',
    'shift_conditions',
    'shift_condition',
    'shift_der_condition',
    'shift_int_condition',
    'onb_conditions',
    'onb_spectrum',
]
