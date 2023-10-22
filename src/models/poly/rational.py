#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

from ...thirdparty.code import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.constants import *
from ...core.epsilon import *
from .poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'RationalPoly',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@dataclass
class RationalPolyBase:
    numerator: Poly = field(init=True, repr=True)
    denominator: Poly = field(init=True, repr=True)

    def __post_init__(self):
        assert (
            np.max(np.abs(self.denominator.coeff)) > 0
        ), 'The denumerator must be a non-zero polynomial'
        return


class RationalPoly(RationalPolyBase):
    def simplify(self, eps: float = FLOAT_ERR) -> RationalPoly:
        '''
        Reduces rational polynomial p/q.
        '''
        p, q = self.numerator, self.denominator
        zeroes_p, zeroes_q = p.roots, q.roots
        catalogue, [counts_p, counts_q] = duplicates_get_assignment_counts(
            zeroes_p, zeroes_q, eps=eps
        )
        counts = {value: counts_p.get(value, 0) - counts_q.get(value, 0) for value in catalogue}
        counts_p = {value: n for value, n in counts.items() if n > 0}
        counts_q = {value: -n for value, n in counts.items() if n < 0}
        p = p.lead * Poly.from_zeroes(counts_p)
        q = q.lead * Poly.from_zeroes(counts_q)
        return RationalPoly(numerator=p, denominator=q)
