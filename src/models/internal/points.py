#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ...thirdparty.data import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.poly import *
from ..generated.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_normalisation_params',
    'get_renormalised_polynomial',
    'get_renormalised_polynomial_time_only',
    'get_renormalised_polynomial_values_only',
    'get_renormalised_data',
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


def get_renormalised_polynomial(
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


def get_renormalised_polynomial_time_only(
    info: FittedInfo,
) -> list[float]:
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    deg = len(coeff) - 1
    Tpow = np.cumprod([1] + [T] * deg)
    coeff_rescaled = [s * cc / TT for cc, TT in zip(coeff, Tpow)]
    return coeff_rescaled


def get_renormalised_polynomial_values_only(
    info: FittedInfo,
) -> list[float]:
    '''
    Normalisation:
    ```
    z(t) = (x(t₀ + T·t) - (c + mt))/s
    ```
    Unnormalisation (but write polynomial centred on `t₀` instead of `0`):
    ```
    x(T·t) = c + m · (t-t₀) + s · z(t-t₀)
    ```
    '''
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    coeff_rescaled = [s * cc for cc in coeff]
    coeff_rescaled[0] += c
    coeff_rescaled[1] += m
    return coeff_rescaled


def get_renormalised_data(
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
    t_split: float = 0.0,
) -> pd.DataFrame:
    t_new = []
    x_new = []
    t = data['time'].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)

    # get common parameters
    _, info0 = fitinfos[-1]
    T0, c0, m0, s0 = get_normalisation_params(info0)

    # renormalise all cycles
    for (i1, i2), info in fitinfos[:-1]:
        T, c, m, s = get_normalisation_params(info)
        # normalise time and points for cycle
        # NOTE: normalise t, then x!
        tt = (t[i1:i2] - t[i1]) / T
        xx = (x[i1:i2] - (c + m * tt)) / s
        # unnormlalise based on common parameters
        # NOTE: unnormalise x, then t!
        xx = c0 + m0 * tt + s0 * xx
        tt = T0 * tt
        # store
        t_new += tt.tolist()
        x_new += xx.tolist()

    # split times
    t_new = np.asarray(t_new)
    t = t_new + T * (t_new < t_split) - t_split

    # store in new data structure
    data = pd.DataFrame({'time[orig]': t_new, 'time': t, quantity: x_new}).astype(
        {'time[orig]': 'float', 'time': 'float', quantity: 'float'}
    )
    return data
