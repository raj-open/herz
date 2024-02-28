#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
NOTE:
The main method in this script computes the Fourier transform
of polynomials.
To achieve this, it suffices to just consider monomials.

Computation
~~~~~~~~~~~
   Set

   ```text
   F[tᵏ](n) := ∫_{t ∈ [0, 1]} tᵏ exp(-st) dt,
   ```

   where `s = ι2πn`, `n ∈ ℤ`.
   Then

   ```text
   s·sᵏ/k!·F[tᵏ](n) = ∫_{t ∈ [0, 1]} (st)ᵏ/k!·s·exp(-st) dt
       = -∫_{t ∈ [0, 1]} (st)ᵏ/k! · d/dt exp(-st) dt
       = -[(st)ᵏ/k! · exp(-st)] + ∫_{t ∈ [0, 1]} (d/dt (st)ᵏ/k!) exp(-st) dt
       = -[exp(-s) – 0]·sᵏ/k! + s·∫_{t ∈ [0, 1]} (st)ᵏ¯¹/(k-1)! exp(-st) dt
       = -sᵏ/k! + s·(st)ᵏ¯¹/(k-1)!·F[tᵏ¯¹](n)
       (since s = ι2πn, n ∈ ℤ)
   ```

   The recursion resolves to:

   ```text
   F[k](n) = -1/s · ∑_{j=1}^{k} sʲ/j! / (sᵏ/k!)
       = -1/g ·∑_{j=1}^{k} (gʲ/j!)/(gᵏ/k!) nʲ / nᵏ⁺¹
   ```

   for `n ≠ 0`, and all `k ≥ 0`,
   where g = ι2π.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.types import *

from .poly import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fourier_of_polynomial',
    'integral_poly_trig',
    'integral_poly_exp',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


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
    #    coeffs_exp[i] = (-g))^i / i! for 1 ≤ i ≤ deg
    #    coeffs_top[:, 0] = 0
    #    coeffs_top[i, k] =
    #      { 0  :  0 ≤ i ≤ deg - k
    #      { -coeffs_exp[i-(deg - k)] / coeffs_exp[k]
    #      {    : deg - k + 1 ≤ i ≤ deg
    #    for k > 0
    #
    # where g = -ι2π.
    # Then coeff_top[i] = ∑ₖ cₖ·Tᵏ·coeffs_top[i, k]
    # --------
    g = -1j * 2 * pi
    coeffs_exp = np.cumprod(-g / np.asarray(range(1, deg + 1)))
    coeffs_top = np.asarray(
        [
            [0] * (deg - k + 1) + normalise_leading_coeff(coeffs_exp[:k])
            for k in range(0, deg + 1)
        ]
    ).T
    coeff_top = ((coeffs_top @ p_scaled) / g).tolist()
    coeff_bot = [0] * (deg + 1) + [1.0]

    return F0, coeff_top, coeff_bot


def integral_poly_trig(
    omega: float,
    p: Iterable[float],
    t1: float,
    t2: float,
) -> tuple[float, float]:
    '''
    Returns `x, y`, where
    ```
    x = ∫ p(t) cos(ωt) dt = Re ∫ p(t) exp(ιωt) dt
    y = ∫ p(t) sin(ωt) dt = Im ∫ p(t) exp(ιωt) dt
    ```
    where the integrals are computed over `t in [t1, t2]`.
    '''
    I = integral_poly_exp(s=1j * omega, p=p, t1=t1, t2=t2)
    return I.real, I.imag


def integral_poly_exp(
    s: complex,
    p: Iterable[float],
    t1: float = 0.0,
    t2: float = 1.0,
) -> complex:
    '''
    Computes `∫ p(t) exp(st) dt` over `t in [t₁, t₂]`

    **NOTE:**
    ```
    ∫ p(t) exp(st) dt
    over t in [t₁, t₂]
    = ∆t·exp(s·t₁) · ∫ p(t₁ + ∆t·u) exp(s·∆t·u) du
      over u in [0, 1]
    ```
    Thus, upon rescaling, it suffices to compute integrals from 0 to 1.
    '''
    deg = len(p) - 1

    # rescale
    if not (t1 == 0 and t2 == 1):
        dt = t2 - t1
        scale = np.cumprod([1] + [dt] * deg)
        c = dt * np.exp(s * t1)
        p = scale * get_recentred_coefficients(coeff=p, t0=t1)
        s = s * dt
        return c * integral_poly_exp(s=s, p=p)

    deg = len(p) - 1
    I = [0] * (deg + 1)

    # compute vectors t_j = t ^ j
    indices = np.asarray(range(deg + 1))
    dirac = np.asarray([1] + [0] * deg)
    one = np.asarray([1] * (deg + 1))

    if s == 0:
        # determine integals I_i := ∫ t^i exp(st) dt
        I = one / (indices + 1)
    else:
        # compute C_ij := coeff j of exp_i(-s) / coeff i of exp_i(-s)
        # where exp_i(...) = exp-series truncated to polynomial of degree i.
        coeffs_exp = np.cumprod(-s / np.asarray(range(1, deg + 1)))
        coeffs_exp = np.insert(coeffs_exp, 0, 1)
        coeffs = np.asarray([coeffs_exp] * (deg + 1))
        mask = np.asarray([1 * (indices <= k) for k in range(deg + 1)])
        coeffs = mask * coeffs
        coeffs = np.diag(1 / np.diag(coeffs)) @ coeffs

        # determine integals I_i := ∫ t^i exp(st) dt
        u = (one * np.exp(s) - dirac) / s
        I = coeffs @ u

    # compute integral ∫ p(t) exp(st) dt
    I = np.inner(p, I)

    return I


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def normalise_leading_coeff(
    p: Iterable[complex],
    c_lead: complex = 1.0,
) -> list[complex]:
    if not isinstance(p, np.ndarray):  # pragma: no cover
        p = np.asarray(p)
    p_scaled = p.copy()
    if len(p_scaled) > 0:
        p_scaled *= c_lead / p_scaled[-1]
    return p_scaled.tolist()
