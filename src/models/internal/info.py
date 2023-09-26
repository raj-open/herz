#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.poly import *
from ..generated.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_normalisation_params',
    'get_rescaled_polynomial',
    'get_rescaled_polynomial_and_points',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - ONB
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_normalisation_params(
    info: FittedInfo,
) -> list[float, float, float, float]:
    params = info.normalisation
    T = params.period
    c = params.intercept
    m = params.gradient
    s = params.scale
    return T, c, m, s


def get_rescaled_polynomial(
    info: FittedInfo,
) -> list[float]:
    '''
    Normalisation:
    ```
    z(t) = (x(t₀ + T·t) - (c + mt))/s
    ```
    Unnormalisation (but write polynomial centred on `t₀` instead of `0`):
    ```
    x(t) = c + m/T · (t-t₀) + s · z((t-t₀)/T)
    ```
    '''
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    deg = len(coeff) - 1
    Tpow = np.cumprod([1] + [T] * deg)
    coeff_rescaled = [s * cc / TT for cc, TT in zip(coeff, Tpow)]
    coeff_rescaled[0] += c
    coeff_rescaled[1] += m / T
    return coeff_rescaled


def get_rescaled_polynomial_and_points(
    info: FittedInfo,
    points: dict[str, list[float]],
) -> tuple[list[float], dict[str, list[float]]]:
    coeff = get_rescaled_polynomial(info)
    T = info.normalisation.period
    points = {key: [T * tt for tt in ts] for key, ts in points.items()}
    return coeff, points
