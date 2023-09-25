#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.physics import *

from ..models.app import *
from ..models.user import *
from . import config

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'output_conversions',
    'output_units',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def output_conversions(columns: list[DataTypeColumn]) -> dict[str, float]:
    '''
    Returns conversion factors
    **from** interal calculations
    **to** desired output units.

    E.g.
    ```py
    # p currently in units for internal computations
    cv = compute_conversions(case)
    p = cv.pressure * p
    # p now in units for outputs
    ```
    '''
    # internal units
    units = config.UNITS
    # throws an error if a unit is missing (we want this behaviour!!)
    units = {col.key: units[col.quantity] for col in columns}
    # compute conversions
    cv = {col.key: convert_units(unitFrom=units[col.key], unitTo=col.unit) for col in columns}
    return cv


def output_units(columns: list[DataTypeColumn]) -> dict[str, str]:
    units = {col.key: col.unit for col in columns}
    return units
