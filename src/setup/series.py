#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..models.app import *
from ..models.internal import *
from . import config

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_polynomial_condition',
    'get_alignment_point',
    'get_alignment_time',
    'get_point_settings',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_polynomial_condition(
    quantity: str,
) -> list[PolyCritCondition | PolyDerCondition | PolyIntCondition]:
    match quantity:
        case 'pressure':
            return config.POLY.pressure[:]
        case 'volume':
            return config.POLY.volume[:]
        case _:
            raise []


def get_alignment_point(quantity: str) -> str:
    match quantity:
        case 'pressure':
            return config.MATCHING.pressure
        case 'volume':
            return config.MATCHING.volume
        case _:
            raise Exception(f'No matching settings defined for {quantity}!')


def get_alignment_time(
    info: FittedInfo, points: dict[str, SpecialPointsConfig], quantity: str
) -> float:
    align = get_alignment_point(quantity)
    T = info.normalisation.period
    t_align = T * points[align].time if align in points else 0.0
    return t_align


def get_point_settings(quantity: str) -> dict[str, SpecialPointsConfig]:
    match quantity:
        case 'pressure':
            return {**config.POINTS.pressure}
        case 'volume':
            return {**config.POINTS.volume}
        case _:
            return {}
