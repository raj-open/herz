#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'integral_interpolated',
    'innerproduct_interpolated',
    'norm_interpolated',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def integral_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = False,
) -> float:
    '''
    Computes integral based on piecewise linear interpolation
    of a discrete time-series (`t`, `x`)
    '''
    t = np.asarray(t.tolist() + [T])

    if periodic:
        x = np.asarray(x.tolist() + [x[0]])
    else:
        x1 = np.asarray(x[1:])
        x2 = np.asarray(x[:-1])
        x = np.concatenate([[x[0]], (x1 + x2) / 2, [x[-1]]])

    dt = np.diff(t)
    x_m = (x[:-1] + x[1:]) / 2
    I = sum(x_m * dt)
    if average:
        I = I / T
    return I


def innerproduct_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = integral_interpolated(t, x * y, T=T, periodic=periodic, average=average)
    return s


def norm_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = innerproduct_interpolated(t, x, x, T=T, periodic=periodic, average=average)
    return np.sqrt(s)
