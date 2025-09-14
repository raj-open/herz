#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np

from ...thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "interpolate_two_series",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def interpolate_two_series(
    t1: NDArray[np.float64],
    x1: NDArray[np.float64],
    t2: NDArray[np.float64],
    x2: NDArray[np.float64],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """
    Takes two time-series defined on `[0, 1)`
    and linearly interpolates them to a common time axis.
    """
    t = sorted(set(t1.tolist() + t2.tolist()))
    t = np.asarray(t)
    dt = np.diff(t)
    dt = np.concatenate([dt[:1], dt, dt[-1:]])
    dt = (dt[:-1] + dt[1:]) / 2
    x1 = np.interp(t, xp=t1, fp=x1, left=x1[0], right=x1[-1])
    x2 = np.interp(t, xp=t2, fp=x2, left=x2[0], right=x2[-1])
    return t, dt, x1, x2
