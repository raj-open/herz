#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import math

import numpy as np

from ....core.log import *
from ....models.fitting import *
from ....models.polynomials import *
from ....thirdparty.maths import *
from .parameters import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "get_bounds_from_settings",
    "get_initialisation_from_settings",
    "get_schema_from_settings",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_schema_from_settings(
    schema: dict[str, str],
    env: dict[str, float],
) -> dict[str, float]:
    """
    Determines schema for time-values
    """
    env = env | {"math": math, "np": np}
    env_ = {}
    for key, expr in schema.items():
        try:
            env_[key] = eval(expr, env | env_)
        except Exception as err:
            raise ValueError(f"Could not evaluate environment value {key}: {expr}. {err}")
    return env_


def get_bounds_from_settings(
    conditions: list[FitTrigCondition],
    env: dict[str, float],
) -> tuple[float, float]:
    invscale_min = 0
    invscale_max = np.inf

    try:
        env = env | {"math": math, "np": np}
        for cond in conditions:
            value: float = eval(cond.value, env)
            match cond.kind:
                case EnumBoundKind.HSCALE_LOWER_BOUND:
                    invscale_max = min(invscale_max, 1 / value)
                case EnumBoundKind.INVHSCALE_UPPER_BOUND:
                    invscale_max = min(invscale_max, value)
                case EnumBoundKind.HSCALE_UPPER_BOUND:
                    invscale_min = max(invscale_min, 1 / value)
                case EnumBoundKind.INVHSCALE_LOWER_BOUND:
                    invscale_min = max(invscale_min, value)

    except Exception as err:
        raise ValueError(f"Could not interpret conditions! {err}")

    return invscale_min, invscale_max


def get_initialisation_from_settings(
    conds: FitExpIntialisation,
    env: dict[str, float],
) -> FittedInfoExp:
    try:
        env = env | {"math": math, "np": np}
        beta: float = eval(str(conds.beta), env)
        vscale: float = eval(str(conds.vscale), env)
        vshift: float = eval(str(conds.vshift), env)
    except Exception as err:
        raise ValueError(f"Could not interpret conditions! {err}")

    return FittedInfoExp(
        hscale=1 / beta,
        vshift=vshift,
        vscale=vscale,
    )


# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def xintercept(
    PQ1: tuple[tuple[float, float], tuple[float, float]],
    PQ2: tuple[tuple[float, float], tuple[float, float]],
) -> float:
    C1, m1 = line_model(*PQ1)
    C2, m2 = line_model(*PQ2)
    x = -(C2 - C1) / (m2 - m1)
    return x


def yintercept(
    PQ1: tuple[tuple[float, float], tuple[float, float]],
    PQ2: tuple[tuple[float, float], tuple[float, float]],
) -> float:
    C1, m1 = line_model(*PQ1)
    C2, m2 = line_model(*PQ2)
    y = (C2 * m1 - C1 * m2) / (m1 - m2)
    return y


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def line_model(
    P: tuple[float, float],
    Q: tuple[float, float],
) -> tuple[float, float]:
    (x1, y1) = P
    (x2, y2) = Q
    m = (y2 - y1) / (x2 - x1)
    C = y1 - m * x1
    return C, m
