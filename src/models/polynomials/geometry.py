#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import math
from collections.abc import Iterable
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

from ...core.constants import *
from ...thirdparty.maths import *
from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "inner_product_poly_exp",
    "inner_product_polybasis",
    "norm_poly_exp",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS, VARIABLES
# ----------------------------------------------------------------

T = TypeVar("T")

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def inner_product_poly_exp(
    f: PolyExp[T],
    g: PolyExp[T],
    *intervals: tuple[float, float],
) -> T:
    """
    Computes the inner product ⟨f, g⟩
    over a space determined by a series of (assumed) disjoint intervals.
    """
    # determine integrand
    h = f * g.conjugate()
    # determine a stem-function
    H = h.integral()
    # compute stem-function at all endpoints of the intervals
    times = [a for a, b in intervals] + [b for a, b in intervals]
    H_values = H.values(times)
    # add up the differences (= integrals over all each interval)
    N = len(intervals)
    Integ = sum(H_values[N:] - H_values[:N])
    return Integ


def norm_poly_exp(
    f: PolyExp,
    *intervals: tuple[float, float],
):
    """
    Computes the L²-norm ‖f‖
    over a space determined by a series of (assumed) disjoint intervals.
    """
    return math.sqrt(inner_product_poly_exp(f, f, *intervals))


# ----------------------------------------------------------------
# METHODS - Vectorised
# ----------------------------------------------------------------


def inner_product_polybasis(
    B: NDArray[np.float64],
    intervals: Iterable[tuple[float, float]],
) -> NDArray[np.float64]:
    """
    Computes interproducts of polynomials.
    @returns
    matrix `S` with

    ```
    S[i, j] = ∫_[t1, t2] p_i · p_j^* dt
    ```

    for each `i, j ∈ {0, 1, 2, …, m}`
    """
    d = B.shape[0] - 1
    m = B.shape[1]
    ip = get_inner_products_standard_basis(d, d, intervals)
    S = np.zeros((m, m))

    for j1 in range(m):
        for j2 in range(m):
            # NOTE: coeffs[i, k] = B[i, j1]·B*[j2, k]*
            # sum(coeffs) = ∑_{i,k} B[i, j1]·B*[j2, k]*
            # = ∑_{i,k} 1^T·B[i, j1]·B*[j2, k]*·1
            coeffs = B[:, j1][:, np.newaxis] * B[:, j2][np.newaxis, :].conj()
            S[j1, j2] = np.sum(ip * coeffs)

    return S


# ----------------------------------------------------------------
# AUXILLIARY METHODS
# ----------------------------------------------------------------


def get_inner_products_standard_basis(
    d1: int,
    d2: int,
    intervals: Iterable[tuple[float, float]],
):
    """
    Computes the inner products between the elements of the standard basis.
    """
    powers1 = np.asarray(range(d1 + 1))
    powers2 = np.asarray(range(d2 + 1))
    sumpowers = powers1[:, np.newaxis] + powers2[np.newaxis, :] + 1

    ip = np.zeros((d1 + 1, d2 + 1))
    for t1, t2 in intervals:
        ip += t2**sumpowers - t1**sumpowers
    ip /= sumpowers

    return ip
