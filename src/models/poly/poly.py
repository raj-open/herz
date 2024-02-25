#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from ...thirdparty.code import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.utils import *
from ...core.constants import *
from ...core.epsilon import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Poly',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar('NUMBER', float, complex)
T = TypeVar('T', covariant=True, bound=complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


@dataclass
class PolyBase(Generic[T]):
    coeff: list[T] = field(init=True, repr=False)
    lead: T = field(init=False, repr=True)
    degree: int = field(init=False, repr=True)
    _roots: list[complex] = field(init=False, repr=False)

    def __post_init__(self):
        while len(self.coeff) > 0 and self.coeff[-1] == 0:
            self.coeff = self.coeff[:-1]
        if len(self.coeff) == 0:
            self.coeff = [0]
        self.lead = self.coeff[-1]
        self.degree = len(self.coeff) - 1
        if self.degree > 0:
            self.roots = np.roots(list(self.coeff)[::-1]).tolist()
            self.roots = eps_clean_zeroes(self.roots, eps=SOLVE_ERR)
        else:
            self.roots = []
        return

    @property
    def roots(self) -> list[complex]:
        return self._roots

    @roots.setter
    def roots(self, values: list[complex]):
        self._roots = sorted(values, key=lambda x: (x.real, abs(x.imag), x.imag))
        return


class Poly(PolyBase[T]):
    @staticmethod
    def from_zeroes(
        zeroes: dict[T, int] | list[T],
        lead: T = 1.0,
    ) -> Poly[T]:
        p = Poly(coeff=[lead])
        if isinstance(zeroes, list):
            for z in zeroes:
                p *= Poly([-z, 1])
            p.roots = zeroes
        else:
            for z, n in zeroes.items():
                assert n >= 0, 'Cannot multiply by negative powers!'
                if n == 0:
                    continue
                z_pow = np.cumprod([1] + [-z] * n)
                p *= Poly([math.comb(n, k) * zz for k, zz in zip(range(n + 1), z_pow[::-1])])
            p.roots = flatten(*[[z] * n for z, n in zeroes.items()])
        return p

    @staticmethod
    def pre_compare(p: Poly[T], q: Poly[T]) -> tuple[list[T], list[T]]:
        m = len(p.coeff)
        n = len(q.coeff)
        N = max(m, n)
        coeff_p = p.coeff + [0] * (N - m)
        coeff_q = q.coeff + [0] * (N - n)
        return coeff_p, coeff_q

    @property
    def real(self) -> Poly[float]:
        return Poly(coeff=[c.real for c in self.coeff])

    @property
    def imag(self) -> Poly[float]:
        return Poly(coeff=[c.imag for c in self.coeff])

    def conjugate(self) -> Poly[T]:
        return Poly(coeff=[c.conjugate() for c in self.coeff])

    def __copy__(self) -> Poly:
        return Poly(self.coeff)

    def __deepcopy__(self) -> Poly:
        return self.__copy__()

    def __eq__(self, o: Any) -> bool:
        coeff_p = self.coeff
        if isinstance(o, (int, float, complex)):
            return self.__eq__(Poly(coeff=[o]))
        if isinstance(o, Poly):
            coeff_p, coeff_q = Poly.pre_compare(self, o)
            return all(c == cc for c, cc in zip(coeff_p, coeff_q))
        return False

    def __add__(self, q: Any) -> Poly[T]:
        if isinstance(q, (int, float, complex)):
            result = self + Poly(coeff=[q])
            if q == 0:
                result.roots = self.roots
        if isinstance(q, Poly):
            coeff, coeff_q = Poly.pre_compare(self, q)
            result = Poly(coeff=[c + cc for c, cc in zip(coeff, coeff_q)])
            if q.lead == 0:
                result.roots = self.roots
        raise TypeError(f'No addition method for Poly + {type(q)}!')

    def __radd__(self, q: Any) -> Poly:
        return self + q

    def __mul__(self, q: Any):
        if isinstance(q, (int, float, complex)):
            if self.lead == 0 or q == 0:
                return Poly(coeff=[0])
            else:
                result = self * Poly(coeff=[q])
                result.roots = self.roots[:]
        if isinstance(q, Poly):
            if self.lead == 0 or q.lead == 0:
                return Poly(coeff=[0])
            coeff_p = np.asarray(self.coeff)
            coeff = np.sum(
                [
                    [0] * k + (c * coeff_p).tolist() + [0] * (q.degree - k)
                    for k, c in enumerate(q.coeff)
                ],
                axis=0,
            ).tolist()
            result = Poly(coeff=coeff)
            result.roots = self.roots[:] + q.roots[:]
            return result
        raise TypeError(f'No multiplication method for Poly x {type(q)}!')

    def __rmul__(self, q: Any) -> Poly:
        return self * q

    def __pow__(self, o: Any) -> Poly:
        if isinstance(o, int):
            if o < 0:
                raise ValueError(f'Cannot compute Poly ^ {o}!')
            result = Poly(coeff=[1])
            p = Poly(coeff=[1])
            # compues in logarithmic time
            for k, u in enumerate(f'{o:b}'[::-1]):
                if k == 0:
                    p = self.__copy__()
                else:
                    p = p * p
                if u == '1':
                    result *= p
            return result
        raise TypeError(f'Cannot compute Poly ^ {type(o)}!')

    def sq(self) -> Poly[float]:
        roots = self.roots[:] + [z.conjugate() for z in self.roots]
        c = abs(self.lead) ** 2
        p = Poly.from_zeroes(roots, lead=c)
        p = p.real
        p.roots = roots
        return p

    def normalise(self) -> Poly:
        c = self.lead or 1.0
        coeff = [cc / c for cc in self.coeff]
        return Poly(coeff=coeff)

    def derivative(self) -> Poly:
        return Poly([k * c for k, c in enumerate(self.coeff) if k > 0])

    def value(self, t: float) -> NUMBER:
        return Poly([k * c for k, c in enumerate(self.coeff) if k > 0])
