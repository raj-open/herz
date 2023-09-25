#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from .constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'poly',
    'poly_single',
    'get_real_polynomial_roots',
    'derivative_coefficients',
    'integral_coefficients',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
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


def poly(t: np.ndarray, *coeff: float) -> np.ndarray:
    N = len(t)
    m = len(coeff)
    x = np.zeros(shape=(N,), dtype=float)
    monom = 1.0
    for k, c in enumerate(coeff):
        x += c * monom
        if k < m - 1:
            monom *= t
    return x


def derivative_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [k * c for k, c in enumerate(coeff) if k >= 1]
    return [nPr(k, n) * c for k, c in enumerate(coeff) if k >= n]


def integral_coefficients(coeff: list[float], n: int = 1) -> list[float]:
    if n == 0:
        return coeff[:]
    if n == 1:
        return [0] + [c / (k + 1) for k, c in enumerate(coeff)]
    return [0] * n + [c / nPr(k + n, n) for k, c in enumerate(coeff)]


def get_real_polynomial_roots(*coeff: float) -> list[float]:
    '''
    Computes reals roots of polynomial with real coefficients.
    NOTE: Roots with algebraic multiplicity = `n` > 1 occur with `n` times in list.
    '''
    roots = np.roots(list(coeff)[::-1]).tolist()
    roots = [t.real for t in roots if abs(t.imag) < FLOAT_ERR]
    # C = sum([ abs(c) for c in coeff ]) or 1.
    # roots = [ t for t in roots if abs(poly_single(t, *coeff)) < C*FLOAT_ERR ]
    return roots
