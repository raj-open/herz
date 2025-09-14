#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import TypeVar

from ...thirdparty.maths import *
from .models_poly import *
from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "integral_poly_trig",
]

# ----------------------------------------------------------------
# LOCAL VARIABLES
# ----------------------------------------------------------------

T = TypeVar("T")

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def integral_poly_trig(
    p: Poly[T],
    omega: float,
    *intervals: tuple[float, float],
) -> tuple[T, T]:
    """
    Consider the polynomial
    ```
    p = a·q
    ```
    where `q` is a polynomial with real-value coefficients.
    Then this method returns `x, y`, where
    ```
    x = ∫ p(t) cos(ωt) dt = a·Re ∫ q(t) exp(ιωt) dt
    y = ∫ p(t) sin(ωt) dt = a·Im ∫ q(t) exp(ιωt) dt
    ```
    where the integrals are computed over `t in [t1, t2]`.
    """
    lead = p.lead
    f = PolyExp(coeff=p.coeff, lead=1, alpha=omega * 1j)
    F = f.integral()
    Integ = F.evaluate(*intervals)
    return lead * Integ.real, lead * Integ.imag
