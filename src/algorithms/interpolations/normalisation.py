#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import math
from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray

from ...thirdparty.maths import *
from .statistics import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "complete_time_series",
    "get_time_aspects",
    "normalise_interpolated_cycle",
    "normalise_to_unit_interval",
]

# ----------------------------------------------------------------
# METHODS - MATHS
# ----------------------------------------------------------------


def get_time_aspects(t: Iterable[float]) -> tuple[int, float, float]:
    """
    Computes aspects

    - `N` - number of points
    - `T` - total duration
    - `dt` - time increment (assuming homogeneity)

    of an ordered series of time points
    """
    match len(t):
        case 0 | 1 as N:
            return N, 1.0, 1.0
        case _ as N:
            # initial guess of dt
            dt = np.median(np.diff(t))
            # correct T_max
            T = (t[-1] + dt) - t[0]
            # (re)compute dt
            dt = T / (N or 1.0)
            return N, T, dt


def complete_time_series(
    t: Iterable[float],
    x: Iterable[float],
    cyclic: bool,
    T: float | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Completes a time series (t,x) to include an endpoint.
    If `cyclic == true`, the endpoint repeats the start point.
    Otherwise the data in `x` are simply "blurred" and stretched.
    """
    if T is None:
        _, T, _ = get_time_aspects(t)
    t = np.append(t, t[0] + T)
    if cyclic:
        x = np.concatenate([x, x[:1]])
    else:
        x1 = np.asarray(x[1:])
        x2 = np.asarray(x[:-1])
        x = np.concatenate([[x[0]], (x1 + x2) / 2, [x[-1]]])
    return t, x


def normalise_to_unit_interval(
    t: NDArray[np.float64],
) -> tuple[NDArray[np.float64], int, float, float]:
    N, T, dt = get_time_aspects(t)
    return (t - t[0]) / T, N, T, dt / T


def normalise_interpolated_cycle(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    T: float,
    periodic: bool = False,
) -> tuple[float, float, float, NDArray[np.float64]]:
    # ensure time axis starts at 0
    t = t - t[0]

    # 1. remove linear trend
    # NOTE: disable drift correction
    # m = (x[-1] - x[0]) / (t[-1] - t[0])
    m = 0
    x = x - m * t

    # 2. normalise oscillation
    mu = mean_interpolated(t, x, T=T, periodic=periodic)
    sd = sd_interpolated(t, x, x_mean=mu, T=T, periodic=periodic)
    ampl = math.sqrt(2) * sd
    x = (x - mu) / (ampl or 1.0)

    # 3. remove initial offset
    c = x[0]
    x = x - c

    # 4. correct constants, so that x_orig = c + m * t + s * x
    c = mu + ampl * c
    s = ampl

    return c, m, s, x
