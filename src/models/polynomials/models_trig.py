#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from typing import Generator

from .models_polytrig import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "Cos",
    "Sin",
]

# ----------------------------------------------------------------
# CLASS
# ----------------------------------------------------------------


class Cos(PolyTrig):
    """
    A class to model functions of the form
    ```
    t ⟼ cos(ωt)
    ```
    where `ω` some constant.
    """

    def __init__(self, omega: float, lead: float = 1, **__):
        assert omega != 0
        self.amplitude = lead
        super().__init__(omega=omega, lead=lead, **__)

    @staticmethod
    def cast(model: PolyTrig) -> Cos:
        lead = model.lead.real
        result = Cos(omega=model.omega, lead=lead, **model.params)
        result.roots = []
        return result

    def __copy__(self) -> Cos:
        model = super().__copy__()
        return Cos.cast(model)

    def __deepcopy__(self) -> Cos:
        model = super().__deepcopy__()
        return Cos.cast(model)

    def derivative(self, n: int = 1) -> Cos | Sin:
        model = super().derivative(n)
        return Cos.cast(model) if n % 2 == 0 else Sin.cast(model)

    def integral(self, n: int = 1) -> Cos | Sin:
        model = super().integral(n)
        return Cos.cast(model) if n % 2 == 0 else Sin.cast(model)

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> Cos:
        model = super().rescale(a=a, t0=t0)
        return Cos.cast(model)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[Cos, float, float]]:
        for g, a, b in super().resolve_piecewise(*intervals):
            yield Cos.cast(g), a, b


class Sin(PolyTrig):
    """
    A class to model functions of the form
    ```
    t ⟼ sin(ωt)
    ```
    where `ω` some constant.
    """

    def __init__(self, omega: float, lead: complex = 1, **__):
        assert omega != 0
        self.amplitude = lead
        super().__init__(omega=omega, lead=-1j * lead, **__)

    @staticmethod
    def cast(model: PolyTrig) -> Sin:
        lead = -model.lead.imag
        result = Sin(omega=model.omega, lead=lead, **model.params)
        result.roots = []
        return result

    def __copy__(self) -> Sin:
        model = super().__copy__()
        return Sin.cast(model)

    def __deepcopy__(self) -> Sin:
        model = super().__deepcopy__()
        return Sin.cast(model)

    def derivative(self, n: int = 1) -> Sin | Cos:
        model = super().derivative(n)
        return Sin.cast(model) if n % 2 == 0 else Cos.cast(model)

    def integral(self, n: int = 1) -> Sin | Cos:
        model = super().integral(n)
        return Sin.cast(model) if n % 2 == 0 else Cos.cast(model)

    def rescale(self, a: float = 1.0, t0: float = 0.0) -> Cos:
        model = super().rescale(a=a, t0=t0)
        return Sin.cast(model)

    def resolve_piecewise(
        self,
        *intervals: tuple[float, float],
    ) -> Generator[tuple[Sin, float, float]]:
        for g, a, b in super().resolve_piecewise(*intervals):
            yield Sin.cast(g), a, b
