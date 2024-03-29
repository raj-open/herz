#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.constants import *
from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'inner_product_poly_exp',
    'norm_poly_exp',
    'inner_product_polybasis',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def inner_product_poly_exp(
    f: PolyExp,
    g: PolyExp,
    *intervals: tuple[float, float],
):
    '''
    Computes the inner product ⟨f, g⟩
    over a space determined by a series of (assumed) disjoint intervals.
    '''
    # determine integrand
    h = f * g.conjugate()
    # determine a stem-function
    H = h.integral()
    # compute stem-function at all endpoints of the intervals
    times = [a for a, b in intervals] + [b for a, b in intervals]
    H_values = H.values(times)
    # add up the differences (= integrals over all each interval)
    N = len(intervals)
    I = sum(H_values[N:] - H_values[:N])
    return I


def norm_poly_exp(
    f: PolyExp,
    *intervals: tuple[float, float],
):
    '''
    Computes the L²-norm ‖f‖
    over a space determined by a series of (assumed) disjoint intervals.
    '''
    return math.sqrt(inner_product_poly_exp(f, f, *intervals))


# ----------------------------------------------------------------
# METHODS - Vectorised
# ----------------------------------------------------------------


def inner_product_polybasis(
    B: NDArray[np.float64],
    t1: float = 0.0,
    t2: float = 1.0,
) -> float:
    d = B.shape[0] - 1
    m = B.shape[1]
    ip = get_inner_products_standard_basis(d, d, t1, t2)
    S = np.zeros((m, m))

    for j1 in range(m):
        for j2 in range(j1 + 1):
            # NOTE: coeffs[i, k] = B[i, j1]·B*[j2, k]*
            # sum(coeffs) = ∑_{i,k} B[i, j1]·B*[j2, k]*
            # = ∑_{i,k} 1^T·B[i, j1]·B*[j2, k]*·1
            coeffs = B[:, j1][:, np.newaxis] * B[:, j2][np.newaxis, :].conj()
            S[j1, j2] = np.sum(ip * coeffs)

    for j2 in range(m):
        for j1 in range(j2):
            S[j1, j2] = S[j2, j1]
    return S


# ----------------------------------------------------------------
# AUXILLIARY METHODS
# ----------------------------------------------------------------


def get_inner_products_standard_basis(
    d1: int,
    d2: int,
    t2: float = 1.0,
    t1: float = 0.0,
):
    '''
    Computes the inner products between the elements of the standard basis.
    '''
    powers1 = np.asarray(range(d1 + 1))
    powers2 = np.asarray(range(d2 + 1))
    sumpowers = powers1[:, np.newaxis] + powers2[np.newaxis, :] + 1

    match t1:
        case 0.0:
            tt1 = np.zeros((d1 + 1, d2 + 1))
        case 1.0:
            tt1 = np.ones((d1 + 1, d2 + 1))
        case _:
            tt1 = t1**sumpowers

    match t2:
        case 0.0:
            tt2 = np.zeros((d1 + 1, d2 + 1))
        case 1.0:
            tt2 = np.ones((d1 + 1, d2 + 1))
        case _:
            tt2 = t2**sumpowers

    T = t2 - t1 or 1.0
    ip = (tt2 - tt1) / (T * sumpowers)
    return ip
