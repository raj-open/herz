#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from math import pi

import numpy as np

from ...thirdparty.maths import *
from .models_poly import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fourier_of_polynomial",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fourier_of_polynomial(
    p: Poly,
    t1: float = 0,
    t2: float = 1,
) -> tuple[float, Poly[complex]]:
    r"""
    Let `F` be defined by

    ```text
    F(n) = 1/T ∫_{t ∈ [t₁, t₂]} p(t) exp(-ι2πnt/T) dt.
    ```
    where `T = t₂ - t₁`.

    After renormalising, one can assume `t₁=0` and `t₂=1`.

    Consider `p(t) = tᵏ` for some `k ∈ ℕ₀`.
    For `n ∈ ℤ \\ {0}` one has

    ```
    F(n) = ∫ tᵏ·e^{-ι2πnt} dt
    = -(exp_{k}(-s) e^{s} - 1) / ((-s)ᵏ⁺¹/k!)
      with s = -ι2πn = -gn, g = ι2π
    = -(exp_{k}(gn) - 1) / ((gn)ᵏ⁺¹/k!)
    = -∑ⱼ gʲ/j! / ((gn)ᵏ⁺¹/k!) sum over j = 1 ... k
    = -1/g ∑ⱼ (gʲ/j! / (gᵏ/k!)) nʲ⁻ᵏ⁻¹ sum over j = 1 ... k
    = -1/g ∑ⱼ (gᵏ⁺¹⁻ʲ/(k+1-j)! / (gᵏ/k!)) (1/n)ʲ sum over j = 1 ... k
    ```

    NOTE: This is equal to `0` for `k=0`.

    We can thus express `F(n)` as a polynomial in `1/n` for `n ≠ 0`.
    """
    # rescale
    if not (t1 == 0 and t2 == 1):
        """
        ∫ f(t) dt / (t2–t1) from t = t1 to t2
        = ∫ f(a·t + t1) dt from t = 0 to 1
        """
        delta = t2 - t1
        if delta == 0:
            F0 = p(t1)
            return F0, Poly(coeff=[1], lead=0)

        p_ = p.rescale(a=delta, t0=t1 / delta)
        return fourier_of_polynomial(p_, t1=0, t2=1)

    F0 = sum(c / (k + 1) for k, c in enumerate(p.coefficients))

    deg = p.degree
    if deg == 0:
        return F0, Poly(coeff=[0])

    g = 1j * 2 * pi

    indices = np.asarray(range(1, deg + 1))
    zeroes = np.zeros((deg + 1,))

    coeffs_exp = np.cumprod(g / indices)
    E = np.asarray(
        [
            np.concatenate([[0], coeffs_exp[:k][::-1] / coeffs_exp[k - 1], zeroes[: deg - k]])
            for k in range(1, deg + 1)
        ]
    ).T

    coeffs_p = np.asarray(p.coefficients)
    coeffs_F = (E @ coeffs_p[1:]) / -g

    F = Poly(coeff=coeffs_F.tolist())

    return F0, F
