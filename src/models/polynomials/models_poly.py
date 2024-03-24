#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations
from ...thirdparty.maths import *
from ...thirdparty.types import *

from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Poly',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', float, complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class Poly(PolyExp[T]):
    '''
    A class to model (possibly periodic) polynomials.
    '''

    def __init__(self, coeff: list[T], lead: complex = 1, **__):
        super().__init__(lead=lead, coeff=coeff, alpha=0, **__)

    @staticmethod
    def cast(model: PolyExp[T]) -> Poly[T]:
        return Poly(lead=model.lead, coeff=model.coeff, **model.params)

    @staticmethod
    def value(coeff: Iterable[T], t: float, **__) -> T:
        p = Poly[T](coeff=coeff, **__)
        return p(t)

    def __copy__(self) -> Poly[T]:
        return Poly[T](**self.serialise())

    def __deepcopy__(self) -> Poly[T]:
        return self.__copy__()

    def __add__(self, q: Any) -> Poly:
        if isinstance(q, (int, float, complex)):
            result = self + Poly(coeff=[q], accuracy=self.accuracy)
            if q == 0:
                result.roots = self.roots

        if isinstance(q, Poly):
            params = self.params
            match self.cyclic, q.cyclic:
                case True, True:
                    assert self.offset == q.offset, 'Models must have compatible offset-value!'
                    assert self.period == q.period, 'Models must have compatible period-value!'
                case False, True:
                    params = q.params

            coeff, coeff_q = pre_compare(self, q)
            params = params | {'accuracy': max(self.accuracy, q.accuracy)}
            result = Poly(load=1, coeff=[c + cc for c, cc in zip(coeff, coeff_q)], **params)
            match self.lead == 0, q.lead == 0:
                case True, True:
                    result.roots = []
                case True, _:
                    result.roots = q.roots
                case _, True:
                    result.roots = self.roots

            return result

        raise TypeError(f'No addition method for Poly + {type(q)}!')

    def __radd__(self, q: Any) -> Poly:
        return self + q

    def __copy__(self) -> Poly[T]:
        model = super().__copy__()
        return Poly[T].cast(model)

    def __deepcopy__(self) -> Poly[T]:
        model = super().__deepcopy__()
        return Poly[T].cast(model)

    def __call__(self, t: float) -> T:
        return super().__call__(t)

    def values(self, t: Iterable[float]) -> NDArray[np.float]:
        return super().values(t)

    def derivative(self, n: int = 1) -> Poly[T]:
        f = super().derivative(n)
        return Poly[T].cast(f)

    def integral(self, n: int = 1) -> Poly[T]:
        f = super().integral(n)
        return Poly[T].cast(f)

    def evaluate(self, *intervals: tuple[float, float]) -> T:
        return super().evaluate(*intervals)

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> Poly[T]:
        f = super().rescale(a=a, t0=t0)
        return Poly[T].cast(f)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[Poly[T], float, float]]:
        for g, a, b in super().resolve_piecewise(*intervals):
            yield Poly[T].cast(g), a, b
