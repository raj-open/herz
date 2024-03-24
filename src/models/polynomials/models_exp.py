#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations
from ...thirdparty.types import *

from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Exp',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T', float, complex)

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class Exp(PolyExp[T]):
    '''
    A class to model functions of the form
    ```
    t ⟼ exp(αt)
    ```
    where `α` some constant.
    '''

    def __init__(self, alpha: complex, lead: T = 1, **__):
        super().__init__(alpha=alpha, lead=lead, coeff=[1], **__)

    @staticmethod
    def cast(model: PolyExp[T]) -> Exp[T]:
        return Exp[T](alpha=model.alpha, lead=model.lead, **model.params)

    def __copy__(self) -> Exp[T]:
        return Exp[T](**self.serialise())

    def __deepcopy__(self) -> Exp[T]:
        return self.__copy__()

    def derivative(self, n: int = 1) -> Exp[T]:
        f = super().derivative(n)
        return Exp[T].cast(f)

    def integral(self, n: int = 1) -> Exp[T]:
        f = super().integral(n)
        return Exp[T].cast(f)

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> Exp:
        f = super().rescale(a=a, t0=t0)
        return Exp[T].cast(f)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[Exp[T], float, float]]:
        for g, a, b in super().resolve_piecewise(*intervals):
            yield Exp[T].cast(g), a, b
