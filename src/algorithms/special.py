#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *

from ..core.log import *
from ..core.poly import *
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'recognise_special_points_pressure',
    'recognise_special_points_volume',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def recognise_special_points_pressure(info: FittedInfo) -> dict[str, float]:
    # NOTE: see documentation/README.md for definitions.
    # TODO: implement this
    log_warn('Classification of pressure points not yet implemented!')
    return {}


def recognise_special_points_volume(info: FittedInfo) -> dict[str, float]:
    # NOTE: see documentation/README.md for definitions.
    # TODO: implement this
    log_warn('Classification of volume points not yet implemented!')
    return {}
