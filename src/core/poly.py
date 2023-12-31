#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.types import *

from .utils import *
from .constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'poly',
    'poly_single',
    'print_poly',
    'get_real_polynomial_roots',
    'get_recentred_coefficients',
    'get_derivative_coefficients',
    'get_integral_coefficients',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - basic
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def poly_single(t: float, *coeff: float) -> float:
    m = len(coeff)
    x = 0.0
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


def poly(t: Iterable[float], *coeff: float) -> np.ndarray:
    t = np.asarray(t)
    N = len(t)
    m = len(coeff)
    x = np.zeros(shape=(N,), dtype=float)
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - strings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def print_poly(coeff: list[float], var: str = 'X', unitise: bool = True) -> str:
    monoms = [(k, c) for k, c in enumerate(coeff) if c != 0]
    expr = '0'

    def coeff_pow_f(obj: tuple[int, float]) -> str:
        k, c = obj
        c_str = f'{c:.4f}'
        if k == 0:
            return c_str
        if k == 1:
            return f'{c_str} * {var}'
        return f'{c_str} * {var}^{k}'

    def coeff_pow_g(obj: tuple[int, float]) -> str:
        k, c = obj
        c_str = f'{c:.4g}'
        if k == 0:
            return c_str
        if k == 1:
            return f'{c_str} * {var}'
        return f'{c_str} * {var}^{k}'

    match len(monoms):
        case 0:
            expr = '0'
        case 1:
            expr = coeff_pow_g(monoms[-1])
        case _:
            (n, c_leading) = monoms[-1]
            if unitise:
                expr = ' + '.join([coeff_pow_f((k, c / c_leading)) for k, c in monoms])
                match c_leading:
                    case 1:
                        expr = expr
                    case -1:
                        expr = '-' + expr
                    case _:
                        expr = f'{c_leading:.4g} * ({expr})'
            else:
                expr = ' + '.join([coeff_pow_g(obj) for obj in monoms])
    return expr


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - algebra
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_real_polynomial_roots(coeff: list[float]) -> list[float]:
    '''
    Computes reals roots of polynomial with real coefficients,
    sorted in ascending order.

    For constant polynomials the empty set is returned, even for the 0-polynomial.

    NOTE: Roots with algebraic multiplicity = `n` > 1 occur with `n` times in list.
    '''
    if len(coeff) <= 1:
        return []

    roots = np.roots(list(coeff)[::-1]).tolist()
    roots = [t.real for t in roots if abs(t.imag) < MACHINE_EPS]
    # C = sum([ abs(c) for c in coeff ]) or 1.
    # roots = [ t for t in roots if abs(poly_single(t, *coeff)) < C*MACHINE_EPS ]
    roots = sorted(roots)
    return roots


def get_recentred_coefficients(coeff: list[float], t0: float) -> list[float]:
    '''
    Let `p` be a `d`-degree polynomial.
    Computes coeffients of p(t) expressed as
    ```
    p(t) = ∑ₖ cₖ·(t - t₀)ᵏ
    ```
    To do this, observe
    ```
    ∑ₖ cₖ·tᵏ = p(t + t₀)
        = ∑ⱼ aⱼ·(t + t₀)ʲ
        = ∑ⱼ aⱼ·∑ₖ (j choose k) t₀ʲ⁻ᵏtᵏ
        = ∑ₖ (∑ⱼ (j choose k) aⱼ·t₀ʲ⁻ᵏ) tᵏ
        = ∑ₖ (∑ⱼ (k+j choose k) aₖ₊ⱼ·t₀ʲ) tᵏ
    ```
    Let `A` be the `(d+1) x (d+1)` top-left-diagonal matrix with
    ```
    A[k, j] = (k+j choose k) aₖ₊ⱼ for 0 ≤ j ≤ d - k
    A[k, j] = 0 for d-k < j ≤ d
    ```
    and let `u` be the `d+1`-dim vector
    ```
    u[j] = t₀ʲ
    ```
    Then
    ```
    (A·u)[k] = ∑ⱼ A[k, j] u[j] from j = 0 to d-k
        = ∑ⱼ (k+j choose k) aⱼ₊ₖ·t₀ʲ
        = cₖ
    ```
    for each k.
    '''
    deg = len(coeff) - 1
    A = np.asarray(
        [[nCr(k + j, k) * a for j, a in enumerate(coeff[k:])] + [0] * k for k in range(deg + 1)]
    )
    u = np.cumprod([1] + [t0] * deg)
    coeff_recentred = (A @ u).tolist()
    return coeff_recentred


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - calculus
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_derivative_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [k * c for k, c in enumerate(coeff) if k >= 1]
    return [nPr(k, n) * c for k, c in enumerate(coeff) if k >= n]


def get_integral_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [0] + [c / (k + 1) for k, c in enumerate(coeff)]
    return [0] * n + [c / nPr(k + n, n) for k, c in enumerate(coeff)]
