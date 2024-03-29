#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations
from ...thirdparty.code import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ..epsilon import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'PolyExpBase',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', float, complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


@dataclass
class PolyExpBase(Generic[T]):
    '''
    The base class for poly x exp models.
    '''

    alpha: complex = field(default=0)
    lead: T = field(default=1)
    coeff: list[float] = field(default_factory=lambda: [1])

    # parameters
    # optional periodic behaviour
    cyclic: bool = field(default=False)
    period: float = field(default=1)
    offset: float = field(default=0)
    # accuracy for values of roots
    accuracy: float = field(default=1e-7)

    def __post_init__(self):
        assert self.period > 0, 'Cannot use a non-positive value for the period!'

        while len(self.coeff) > 0 and self.coeff[-1] == 0:
            self.coeff = self.coeff[:-1]

        if len(self.coeff) == 0:
            self.coeff = [0]

        scale = self.coeff[-1]
        if self.lead * scale == 0:
            self.lead = 0
            self.coeff = [1]
        else:
            self.lead *= scale
            self.coeff = [c / scale for c in self.coeff[:-1]] + [1.0]
        return

    def __copy__(self) -> PolyExpBase[T]:
        return PolyExpBase[T](**self.serialise())

    def __deepcopy__(self) -> PolyExpBase[T]:
        return self.__copy__()

    def serialise(self) -> dict:
        return asdict(self)

    @property
    def params(self) -> dict:
        keys = [
            'cyclic',
            'period',
            'offset',
            'accuracy',
        ]
        return {key: getattr(self, key) for key in keys if hasattr(self, key)}

    @property
    def degree(self) -> int:
        return len(self.coeff) - 1

    @property
    def coefficients(self) -> list[T]:
        return [self.lead * c for c in self.coeff]

    @property
    def roots(self) -> list[complex]:
        if not hasattr(self, '_roots'):
            eps = self.accuracy
            if self.degree == 0:
                self._roots = []
            else:
                self._roots = np.roots(list(self.coeff)[::-1]).tolist()
                self._roots = eps_clean_zeroes(self._roots, eps=eps)
        return self._roots

    @property
    def real_roots(self) -> list[float]:
        if not hasattr(self, '_roots_reals'):
            # not necessary, as cleaning already performed!
            # eps = self.accuracy
            # roots = [z.real for z in self.roots if abs(z.imag) < eps]
            roots = [z.real for z in self.roots if z.imag == 0]
            if self.cyclic:
                roots = [
                    self.offset + (t - self.offset) % self.period
                    for t in roots
                    if self.offset <= t and t <= self.offset + self.period
                ]
            self._roots_reals = sorted(roots)
        return self._roots_reals

    @roots.setter
    def roots(self, values: list[complex]):
        self._roots = sorted(values, key=lambda x: (x.real, abs(x.imag), x.imag))
        return
