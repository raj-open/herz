#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
# Exponential fitting of curves #

Fits the following model to data (or a prefitted model thereof)
```
P(V) = a·1 + b·exp(c·V)
```
with parameters `a`, `b`, `c`.
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
    'get_bounds_from_settings',
    'get_initialisation_from_settings',
    'get_schema_from_settings',
    'get_spatial_domain_from_settings',
]
