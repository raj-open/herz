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
    "innerproduct_interpolated",
    "integral_interpolated",
    "norm_interpolated",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def integral_interpolated(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    T: float,
    periodic: bool = False,
) -> float:
    """
    Computes integral based on piecewise linear interpolation
    of a discrete time-series (`t`, `x`)
    """
    t = np.asarray([*t.tolist(), T])

    if periodic:
        x = np.asarray([*x.tolist(), x[0]])

    else:
        x1 = np.asarray(x[1:])
        x2 = np.asarray(x[:-1])
        x = np.concatenate([[x[0]], (x1 + x2) / 2, [x[-1]]])

    dt = np.diff(t)
    x_m = (x[:-1] + x[1:]) / 2
    Integ = sum(x_m * dt)
    return Integ


def innerproduct_interpolated(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = integral_interpolated(t, x * y.conjugate(), T=T, periodic=periodic)
    if average:
        s = s / T
    return s


def norm_interpolated(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = innerproduct_interpolated(t, x, x, T=T, periodic=periodic, average=average)
    return np.sqrt(s)
