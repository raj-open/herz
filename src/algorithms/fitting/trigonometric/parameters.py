#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import math
from math import pi

import numpy as np
from numpy.typing import NDArray

from ....models.fitting import *
from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_trig_parameters_from_info",
    "fit_trig_parameters_to_info",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_trig_parameters_from_info(
    info: FittedInfoTrig,
) -> NDArray[np.float64]:
    """
    Given is the model
    ```
    f(t) = C + b·t + r·cos(ω·(t - t₀))
        = a + b·t + r·cos(ω·t - φ)
            where a = C
            where φ = ω·t₀
        = a + b·t + r·cos(φ)cos(ω·t) + r·sin(φ)·sin(ω·t)
        = a + b·t + c·cos(ω·t) + d·sin(ω·t)
            where
            c = r·cos(φ)
            d = r·sin(φ)
    ```
    """
    a = info.vshift
    b = info.drift
    t0 = info.hshift
    omega = 2 * pi / info.hscale
    phase = omega * t0
    r = info.vscale
    c = r * np.cos(phase)
    d = r * np.sin(phase)
    return np.asarray([a, b, c, d, omega])


def fit_trig_parameters_to_info(x: NDArray[np.float64]) -> FittedInfoTrig:
    """
    Given is the model
    ```
    f(t) = a + b·t + c·cos(ω·t) + d·sin(ω·t)
         = a + b·t + r·cos(φ)cos(ω·t) + r·sin(φ)·sin(ω·t)
            where
            r = |c + ιd|
            φ = Arg(c + ιd)
         = a + b·t + r·cos(ω·t - φ)
         = a + b·t + r·cos(ω·(t - t₀))
            where t₀ = φ / ω
    ```
    """
    a, b, c, d, omega = x
    r = math.sqrt(c**2 + d**2)
    phase = math.atan2(d, c)
    t0 = phase / omega
    return FittedInfoTrig(
        hscale=2 * pi / omega,
        hshift=t0,
        vscale=r,
        vshift=a,
        drift=b,
    )
