#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.code import *
from ...thirdparty.maths import *

from .statistics import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'normalise_to_unit_interval',
    'normalise_interpolated_cycle',
]

# ----------------------------------------------------------------
# METHODS - MATHS
# ----------------------------------------------------------------


def normalise_to_unit_interval(
    t: NDArray[np.float64],
) -> tuple[NDArray[np.float64], float]:
    t_min = min(t)
    t_max = max(t)
    T = t_max - t_min
    t = (t - t_min) / (T or 1.0)
    return t, T


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
