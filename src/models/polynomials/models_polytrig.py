#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from typing import Generator

from .models_polyexp import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "PolyTrig",
]

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class PolyTrig(PolyExp[complex]):
    """
    A class to model functions of the form
    ```
    t ⟼ Re[C·p(t)exp(iωt)]
    ```
    where `ω` = some constant,
    `p` a real-valued polynomial,
    `C` a (possibly complex) leading coefficient.
    """

    def __init__(self, omega: float, coeff: list[float] = [1], lead: complex = 1, **__):
        self.omega = omega
        super().__init__(alpha=1j * omega, lead=lead, coeff=coeff, **__)

    @staticmethod
    def cast(model: PolyExp[complex]) -> PolyTrig:
        omega = model.alpha.imag
        result = PolyTrig(omega=omega, lead=model.lead, coeff=model.coeff, **model.params)
        result.roots = model.roots
        return result

    def __neg__(self) -> PolyTrig:
        model = super().__neg__()
        return PolyTrig.cast(model)

    def __mul__(self, f: Any) -> PolyTrig:
        if isinstance(f, (int, float, complex)):
            pass
        elif isinstance(f, PolyExp) and not isinstance(f, PolyTrig):
            assert f.alpha.real == 0
            assert f.lead.imag == 0
        else:
            raise Exception("No multiplication method developed!")
        model = super().__mul__(f)
        return PolyTrig.cast(model)

    def __rmul__(self, f: Any) -> PolyTrig:
        return self.__mul__(f)

    def __copy__(self) -> PolyTrig:
        model = super().__copy__()
        return PolyTrig.cast(model)

    def __deepcopy__(self) -> PolyTrig:
        model = super().__deepcopy__()
        return PolyTrig.cast(model)

    def __call__(self, t: float) -> float:
        value = super().__call__(t)
        return value.real

    def values(self, t: Iterable[float]):
        value = super().values(t)
        return value.real

    def derivative(self, n: int = 1) -> PolyTrig:
        model = super().derivative(n)
        return PolyTrig.cast(model)

    def integral(self, n: int = 1) -> PolyTrig:
        model = super().integral(n)
        return PolyTrig.cast(model)

    def evaluate(self, *intervals) -> float:
        value = super().evaluate(*intervals)
        return value.real

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> PolyTrig:
        model = super().rescale(a=a, t0=t0)
        return PolyTrig.cast(model)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[PolyTrig, float, float]]:
        for g, a, b in super().resolve_piecewise(*intervals):
            yield PolyTrig.cast(g), a, b
