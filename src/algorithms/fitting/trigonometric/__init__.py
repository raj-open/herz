#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# Trigonometric fitting of curves #

Fits the following model to data (or a prefitted model thereof)
```
f(t) = a·1 + b·t + c·cos(ωt) + d·sin(ωt)
```
with parameters `a`, `b`, `c`, `d`, `ω`.
```
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from .fit import *
from .options import *
from .conditions import *
from .parameters import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fit_options_scale_poly_model',
    'fit_options_scale_data',
    'fit_options_gradients_poly_model',
    'fit_options_gradients_data',
    'fit_trig_parameters_from_info',
    'fit_trig_parameters_to_info',
    'fit_trigonometric_curve',
    'get_bounds_from_settings',
    'get_initialisation_from_settings',
    'get_schema_from_settings',
    'get_spatial_domain_from_settings',
]
