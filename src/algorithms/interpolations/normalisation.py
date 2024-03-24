#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.code import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from .geometry import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'normalise_to_unit_interval',
    'normalise_interpolated_drift',
]

# ----------------------------------------------------------------
# METHODS - MATHS
# ----------------------------------------------------------------


def normalise_to_unit_interval(t: np.ndarray) -> tuple[np.ndarray, float]:
    t_min = min(t)
    t_max = max(t)
    T = t_max - t_min
    t = (t - t_min) / (T or 1.0)
    return t, T


def normalise_interpolated_drift(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
    periodic: bool = False,
) -> tuple[float, float, float, np.ndarray]:
    m = (x[-1] - x[0]) / (t[-1] - t[0])
    c = x[0] - m * t[0]
    x = x - (c + m * t)
    x_max = np.max(abs(x))
    x = x / (x_max or 1.0)
    s = norm_interpolated(t, x, T=T, periodic=periodic, average=True)
    x = x / (s or 1.0)
    s = s * x_max
    return c, m, s, x
