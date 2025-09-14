#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from typing import Generator
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

from ...thirdparty.maths import *
from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "Poly",
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar("T", float, complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class Poly(PolyExp[T]):
    """
    A class to model (possibly periodic) polynomials.
    """

    @staticmethod
    def load_from_zeroes(
        zeroes: list[complex],
        lead: complex = 1.0,
        **__,
    ) -> Poly[complex]:
        result = PolyExp[complex].load_from_zeroes(zeroes=zeroes, lead=lead, **__)
        result = Poly[complex].cast(result)
        return result

    def __init__(self, coeff: list[T], lead: complex = 1, **__):
        super().__init__(lead=lead, coeff=coeff, alpha=0, **__)

    @staticmethod
    def cast(model: PolyExp[T]) -> Poly[T]:
        result = Poly(lead=model.lead, coeff=model.coeff, **model.params)
        result.roots = model.roots
        return result

    @staticmethod
    def value(coeff: Iterable[T], t: float, **__) -> T:
        p = Poly[T](coeff=coeff, **__)
        return p(t)

    def __copy__(self) -> Poly[T]:
        return Poly[T](**self.serialise())

    def __deepcopy__(self) -> Poly[T]:
        return self.__copy__()

    def __neg__(self) -> Poly[T]:
        model = super().__neg__()
        return Poly[T].cast(model)

    def __mul__(self, q: Any) -> Poly:
        result = super().__mul__(q)
        if isinstance(q, (Poly, int, float, complex)):
            result = Poly.cast(result)
        return result

    def __rmul__(self, q: Any) -> Poly:
        return self * q

    def __pow__(self, n: Any) -> Poly[T]:
        model = super().__pow__(n)
        return Poly[T].cast(model)

    def __add__(self, q: Any) -> Poly:
        if isinstance(q, (int, float, complex)):
            result = self + Poly(coeff=[q], accuracy=self.accuracy)
            if q == 0:
                result.roots = self.roots

        if isinstance(q, Poly):
            params = self.params
            match self.cyclic, q.cyclic:
                case True, True:
                    assert self.offset == q.offset, "Models must have compatible offset-value!"
                    assert self.period == q.period, "Models must have compatible period-value!"
                case False, True:
                    params = q.params

            coeff, coeff_q = pre_compare(self, q)
            params = params | {"accuracy": max(self.accuracy, q.accuracy)}
            result = Poly(coeff=[c + cc for c, cc in zip(coeff, coeff_q)], **params)
            match self.lead == 0, q.lead == 0:
                case True, True:
                    result.roots = []
                case True, _:
                    result.roots = q.roots
                case _, True:
                    result.roots = self.roots

            return result

        raise TypeError(f"No addition method for Poly + {type(q)}!")

    def __radd__(self, q: Any) -> Poly:
        return self + q

    def __sub__(self, q: Any) -> Poly:
        if isinstance(q, Poly):
            return self.__add__(-q)
        raise TypeError(f"No addition method for Poly - {type(q)}!")

    def __divmod__(self, q: Poly[T]) -> tuple[Poly[T], Poly[T]]:
        coef_p = np.asarray(self.coefficients)
        coef_q = np.asarray(q.coefficients)
        deg_p = len(coef_p) - 1
        deg_q = len(coef_q) - 1
        s = deg_p - deg_q
        coef_div = [0.0] * max(s + 1, 0)
        while s >= 0:
            a = coef_p[deg_q + s] / coef_q[deg_q]
            coef_div[s] = a
            coef_p[s:] -= a * coef_q
            coef_p = coef_p[:-1]
            s -= 1
        coef_rest = coef_p
        result_div = Poly[T](coeff=coef_div, **self.params)
        result_rest = Poly[T](coeff=coef_rest, **self.params)
        return result_div, result_rest

    def __floordiv__(self, q: Poly[T]) -> Poly[T]:
        p_div_q, _ = divmod(self, q)
        return p_div_q

    def __mod__(self, q: Poly[T]) -> Poly[T]:
        _, rest = divmod(self, q)
        return rest

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
