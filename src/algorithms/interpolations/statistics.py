#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np

from ...thirdparty.maths import *
from .geometry import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "mean_interpolated",
    "sd_interpolated",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def mean_interpolated(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    T: float,
    periodic: bool = False,
) -> float:
    return integral_interpolated(t, x, T=T, periodic=periodic) / T


def sd_interpolated(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    T: float,
    x_mean: float | None = None,
    periodic: bool = False,
) -> float:
    if x_mean is None:
        x_mean = mean_interpolated(t, x, T=T, periodic=periodic)
    return norm_interpolated(t, x - x_mean, T=T, periodic=periodic, average=True)
