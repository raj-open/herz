#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE:
# The main method in this script computes the Fourier transform
# of polynomials.
# To achieve this, it suffices to just consider monomials.
#
# Computation
# ~~~~~~~~~~~
#    Set
#
#    ```text
#    F[tᵏ](n) := ∫_{t ∈ [0, 1]} tᵏ exp(-st) dt,
#    ```
#
#    where `s = ι2πn`, `n ∈ ℤ`.
#    Then
#
#    ```text
#    s·sᵏ/k!·F[tᵏ](n) = ∫_{t ∈ [0, 1]} (st)ᵏ/k!·s·exp(-st) dt
#        = -∫_{t ∈ [0, 1]} (st)ᵏ/k! · d/dt exp(-st) dt
#        = -[(st)ᵏ/k! · exp(-st)] + ∫_{t ∈ [0, 1]} (d/dt (st)ᵏ/k!) exp(-st) dt
#        = -[exp(-s) – 0]·sᵏ/k! + s·∫_{t ∈ [0, 1]} (st)ᵏ¯¹/(k-1)! exp(-st) dt
#        = -sᵏ/k! + s·(st)ᵏ¯¹/(k-1)!·F[tᵏ¯¹](n)
#        (since s = ι2πn, n ∈ ℤ)
#    ```
#
#    The recursion resolves to:
#
#    ```text
#    F[k](n) = -1/s · ∑_{j=1}^{k} sʲ/j! / (sᵏ/k!)
#        = -1/g ·∑_{j=1}^{k} (gʲ/j!)/(gᵏ/k!) nʲ / nᵏ⁺¹
#    ```
#
#    for `n ≠ 0`, and all `k ≥ 0`,
#    where g = ι2π.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.types import *

# from .utils import *
from .poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'fourier_of_polynomial',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def fourier_of_polynomial(
    p: Iterable[float],
    T: float = 1,
) -> tuple[float, list[complex], list[complex]]:
    '''
    @returns Function `F`, where

    ```text
    F[p](n) = 1/T ∫_{t ∈ [0, T]} p(t) exp(-ι2πnt/T) dt.
    ```

    NOTE:

    ```text
    F[tᵏ](n) = 1/T · ∫_{t ∈ [0, T]} tᵏ exp(-ι2πnt/T) dt
        = Tᵏ · ∫_{t ∈ [0, 1]} uᵏ exp(-ι2πnu) du
    '''
    deg = len(p) - 1

    T_pow = np.cumprod([1] + [T] * deg)
    p_scaled = T_pow * np.asarray(p)

    F0 = sum(c / (k + 1) for k, c in enumerate(p_scaled))

    # --------
    # Express Fourier transform as rational function of polynomials:
    # NOTE: We set
    #
    #    coeffs_exp[i] = g^i / i! for 1 ≤ i ≤ deg
    #    coeffs_top[:, 0] = 0
    #    coeffs_top[i, k] =
    #      { 0  :  0 ≤ i ≤ deg - k
    #      { -coeffs_exp[i-(deg - k)] / coeffs_exp[k]
    #      {    : deg - k + 1 ≤ i ≤ deg
    #    for k > 0
    #
    # where g = ι2π.
    # Then coeff_top[i] = ∑ₖ cₖ·Tᵏ·coeffs_top[i, k]
    # --------
    g = 1j * 2 * pi
    coeffs_exp = np.cumprod(g / np.asarray(range(1, deg + 1)))
    coeffs_top = np.asarray(
        [
            [0] * (deg - k + 1) + normalise_leading_coeff(coeffs_exp[:k])
            for k in range(0, deg + 1)
        ]
    ).T
    coeff_top = (-1 / g * (coeffs_top @ p_scaled)).tolist()
    coeff_bot = [0] * (deg + 1) + [1.0]

    return F0, coeff_top, coeff_bot


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def normalise_leading_coeff(
    p: Iterable[complex],
    c_lead: complex = 1.0,
) -> list[complex]:
    if not isinstance(p, np.ndarray):
        p = np.asarray(p)
    p_scaled = p.copy()
    if len(p_scaled) > 0:
        p_scaled *= c_lead / p_scaled[-1]
    return p_scaled.tolist()
