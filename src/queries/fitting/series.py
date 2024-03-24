#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...models.app import *
from ...models.fitting import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_polynomial_condition',
    'get_alignment_point',
    'get_point_settings',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_polynomial_condition(
    quantity: str,
    cfg: PolynomialConfig,
) -> list[PolyCritCondition | PolyDerCondition | PolyIntCondition]:
    match quantity:
        case 'pressure':
            return cfg.pressure[:]
        case 'volume':
            return cfg.volume[:]
        case _:
            raise []


def get_alignment_point(
    quantity: str,
    cfg: MatchingConfig,
) -> str:
    match quantity:
        case 'pressure':
            return cfg.pressure
        case 'volume':
            return cfg.volume
        case _:
            raise Exception(f'No matching settings defined for {quantity}!')


def get_point_settings(
    quantity: str,
    cfg: SpecialPointsConfigs,
) -> dict[str, SpecialPointsConfig]:
    match quantity:
        case 'pressure':
            return {**cfg.pressure}
        case 'volume':
            return {**cfg.volume}
        case _:
            return {}
