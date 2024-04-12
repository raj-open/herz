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

        # to prevent explosion (e.g. upon rescaling), clean up coefficients that are near 0
        self.coeff = remove_small_polynomial_coefficients(self.coeff, eps=self.accuracy)
        scale = self.coeff[-1]
        if self.lead * scale == 0:
            self.lead = 0
            self.coeff = [1]
        else:
            self.lead *= scale
            self.coeff = [c / scale for c in self.coeff[:-1]] + [1]

        [self.lead] = eps_clean_zeroes([self.lead], eps=self.accuracy)
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
            if self.degree == 0:
                values = []
            else:
                values = np.roots(list(self.coeff)[::-1])
                values = clean_and_sort_complex_values(values, eps=self.accuracy)
            self._roots = values
        return self._roots

    @property
    def real_roots(self) -> list[float]:
        if not hasattr(self, '_roots_reals'):
            # not necessary, as cleaning already performed!
            eps = self.accuracy
            roots = [z.real for z in self.roots if abs(z.imag) < eps]
            if self.cyclic:
                roots = [
                    self.offset + (t - self.offset) % self.period
                    for t in roots
                    if self.offset <= t and t <= self.offset + self.period
                ]
            self._roots_reals = sorted(roots)
        return self._roots_reals

    @roots.setter
    def roots(self, values: Iterable[complex]):
        self._roots = clean_and_sort_complex_values(values, eps=self.accuracy)
        return


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def clean_and_sort_complex_values(
    values: Iterable[complex],
    eps: float,
):
    values = eps_clean_pure_real_imaginary(values, eps=eps)
    values = sorted(values, key=lambda x: (x.real, abs(x.imag), x.imag))
    return values


def remove_small_polynomial_coefficients(
    coefficients: Iterable[T],
    eps: float,
) -> list[T]:
    '''
    Renormalises coefficients `c[k]` to the form
    ```
    c[k] = α[k]·t^(n-k)
    ```
    before filtering out "small" values of `α[k]`.
    This is more stable than directly filtering based on `c[k]`,
    as polynomials upon shifting take on the above form.
    '''
    # first remove too small values
    coefficients = np.asarray(coefficients)
    alpha = abs(coefficients)
    filt = alpha < eps
    coefficients[filt] = 0

    # remove all zeroes
    while len(coefficients) > 0 and coefficients[-1] == 0:
        coefficients = coefficients[:-1]
    if len(coefficients) == 0:
        coefficients = [0]

    # compute least-sq fit c[k] ~ α[k]·exp(m·(deg-k))
    deg = len(coefficients) - 1
    coefficients = np.asarray(coefficients)
    indices = np.asarray(range(deg + 1))
    alpha = abs(coefficients)
    filt = alpha >= eps
    C = np.sum((deg - indices[filt]) ** 2)
    m = np.sum((deg - indices[filt]) * np.log(alpha[filt])) / (C or 1)
    alpha = alpha * np.exp(-m * (deg - indices))

    # remove too small values of α[k]
    filt = alpha < eps
    alpha[filt] = 0
    # # remove too small _relative_ values of alpha
    # scale = np.linalg.norm(alpha) / np.sqrt(np.sum(filt) or 1) or 1
    # filt = alpha < (scale * eps)
    # finally, set coefficients
    # alpha[filt] = 0 # <- unnecessary
    coefficients[filt] = 0

    return coefficients
