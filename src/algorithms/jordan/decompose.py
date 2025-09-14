#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...models.polynomials import *
from ...thirdparty.maths import *
from ...thirdparty.types import *
from .polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "algebraic_dimensions",
    "chevalley_polynomial",
    "decompose_jordan_chevalley",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

T = TypeVar("T", np.float64, np.complex128)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def decompose_jordan_chevalley(
    A: NDArray[T],
) -> tuple[
    tuple[NDArray[T], NDArray[T]],
    tuple[NDArray[np.complex128], NDArray[np.complex128]],
]:
    """
    Computes the Jordan–Chevalley (a.k.a. Dunford) decomposition
    of a matrix into diagonalisable and nilpotent parts.
    """
    ch = chevalley_polynomial(A)
    Apow = np.eye(*A.shape)
    D = np.zeros(A.shape)
    for k, a in enumerate(ch.coefficients):
        if k > 0:
            Apow = Apow @ A
        D += a * Apow
    # obtain diagonalisation
    vals, V = np.linalg.eig(D)
    D = np.diag(vals)
    # get nilpotent part
    Vinv = np.linalg.inv(V)
    N = Vinv @ A @ V - D
    return (V, Vinv), (D, N)


def chevalley_polynomial(A: NDArray[T]) -> Poly[np.complex128]:
    """
    Computes the Jordan–Chevalley (a.k.a. Dunford) decomposition
    of a matrix into diagonalisable and nilpotent parts.
    """
    stats = algebraic_dimensions(A)
    data = [(t, Poly(coeff=[-t, 1]) ** n) for t, n in stats.items()]
    return chinese_polynomial(data)


def algebraic_dimensions(
    A: NDArray[T],
) -> Counter[np.complex128]:
    spec = np.linalg.eigvals(A)
    return Counter[T](spec)
