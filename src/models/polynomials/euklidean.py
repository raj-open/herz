#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This submodule contains the Euklidean algorithm.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from .models_poly import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'euklidean_algorithm',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', float, complex)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def euklidean_algorithm(
    p: Poly[T],
    q: Poly[T],
    normalised: bool = True,
) -> tuple[Poly[T], Poly[T], Poly[T]]:
    '''
    Returns polynomials `d`, `m`, `n` such that
    ```
    d = gcd(p, q)
    d = m·p + n·q
    ```

    - If `p`, `q` are 0, then returns `0`, `0`, `0`.
    - Otherwise returns `d` with leading coefficient `1`.
    '''
    if p == 0 and q == 0:
        d = Poly[T](coeff=[1], lead=0)
        factor_p = Poly[T](coeff=[1], lead=0)
        factor_q = Poly[T](coeff=[1], lead=0)
    elif p == 0:
        d = Poly[T](coeff=q.coeff, lead=q.lead)
        factor_p = Poly[T](coeff=[1], lead=0)
        factor_q = Poly[T](coeff=[1])
        if normalised:
            d.lead = 1
            factor_q.lead = 1 / q.lead
    elif q == 0:
        d = Poly[T](coeff=p.coeff, lead=p.lead)
        factor_p = Poly[T](coeff=[1])
        factor_q = Poly[T](coeff=[1], lead=0)
        if normalised:
            d.lead = 1
            factor_p.lead = 1 / p.lead
        else:
            d = Poly[T](coeff=p.coeff, lead=p.lead)
    else:
        p_div_q, r = divmod(p, q)
        d, factor_q, factor_r = euklidean_algorithm(q, r, normalised=normalised)
        factor_q = factor_q - factor_r * p_div_q
        factor_p = factor_r

    return d, factor_p, factor_q
