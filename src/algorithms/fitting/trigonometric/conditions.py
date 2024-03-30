#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.code import *
from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....models.fitting import *
from ....models.polynomials import *
from .parameters import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_schema_from_settings',
    'get_spatial_domain_from_settings',
    'get_bounds_from_settings',
    'get_initialisation_from_settings',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_schema_from_settings(
    schema: dict[str, str],
    env: dict[str, float],
) -> dict[str, float]:
    '''
    Determines schema for time-values
    '''
    env = env | {'math': math, 'np': np}
    env_ = {}
    for key, expr in schema.items():
        try:
            env_[key] = eval(expr, env | env_)
        except Exception as err:
            raise ValueError(f'Could not evaluate environment value {key}: {expr}. {err}')
    return env_


def get_spatial_domain_from_settings(
    intervals_schema: list[list[str]],
    env: dict[str, float],
) -> list[tuple[float, float]]:
    '''
    Determines spatial domain from settings
    '''
    try:
        conv = partial(convert_dom_to_interval, env=env)
        return list(map(conv, intervals_schema))
    except Exception as err:
        raise ValueError(f'Could not interpret intervals! {err}')


def get_bounds_from_settings(
    conditions: list[FitTrigCondition],
    env: dict[str, float],
) -> tuple[float, float]:
    T_min = 1 / 4
    T_max = 4
    try:
        env = env | {'math': math, 'np': np}
        for cond in conditions:
            value: float = eval(cond.value, env)
            match cond.kind:
                case EnumBoundKind.HSCALE_LOWER_BOUND:
                    T_min = max(T_min, value)
                case EnumBoundKind.HSCALE_UPPER_BOUND:
                    T_max = min(T_max, value)

    except Exception as err:
        raise ValueError(f'Could not interpret conditions! {err}')

    # T ≤ ... ⟹ ω ≥ 2π/...
    omega_min = 2 * pi / T_max
    # T ≥ ... ⟹ ω ≤ 2π/...
    omega_max = 2 * pi / T_min

    return omega_min, omega_max


def get_initialisation_from_settings(
    conds: FitTrigIntialisation,
    env: dict[str, float],
) -> NDArray[np.float64]:
    try:
        env = env | {'math': math, 'np': np}
        env = env | {'xintercept': xintercept, 'yintercept': yintercept}
        omega: float = eval(str(conds.omega), env)
        hshift: float = eval(str(conds.hshift), env)
        vscale: float = eval(str(conds.vscale), env)
        vshift: float = eval(str(conds.vshift), env)
        drift: float = eval(str(conds.drift), env)
    except Exception as err:
        raise ValueError(f'Could not interpret conditions! {err}')

    return FittedInfoTrig(
        hshift=hshift,
        hscale=2 * pi / omega,
        vshift=vshift,
        vscale=vscale,
        drift=drift,
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


def convert_dom_to_interval(
    I: RootModel[list[str]],
    env: dict[str, float],
) -> tuple[float, float]:
    '''
    Determines the value of the interval corresponding
    to a spatial configuration of an interval.
    '''
    key1, key2 = I.root
    return (env[key1], env[key2])
