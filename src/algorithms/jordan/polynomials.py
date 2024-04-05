#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...models.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'characteristic_polynomial',
    'chinese_polynomial',
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', int, float, complex)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def characteristic_polynomial(A: np.ndarray) -> Poly[complex]:
    spec = np.linalg.eigvals(A).tolist()
    return Poly[complex].load_from_zeroes(zeroes=spec)


def chinese_polynomial(data: Iterable[tuple[T, Poly[T]]]) -> Poly[T]:
    '''
    @inputs
    list of tuples `(t, q)`, such that

    - `t ∈ K` for some field K;
    - `q ∈ K[X]` are pairwise coprime polynomials.

    @returns
    a polynomial `ch ∈ K[X]` satisfying
    ```
    ch ≡ t mod q
    ```
    for each `(t, q) ∈ data`.
    '''
    ch = Poly[T](coeff=[0])
    for i, (t, q) in enumerate(data):
        if t == 0:
            continue
        # compute product of all polys bar q
        p = Poly[T](coeff=[1])
        for _, q_ in data[:i]:
            p = q_ * p
        for _, q_ in data[i:][1:]:
            p = q_ * p
        # compute gcd
        d, m, n = euklidean_algorithm(p, q, normalised=True)
        # assert d == 1, 'p, q should be coprime'
        # NOTE: 1 = m·p + n·q, so t·m·p ≡ t·1 = t mod q
        ch += t * m * p
    return ch
