#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.thirdparty.unit import *

from src.thirdparty.maths import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="module", autouse=True)
def C() -> float:
    return 8.007


@fixture(scope="module", autouse=True)
def C2() -> float:
    return -0.17


@fixture(scope="module", autouse=True)
def C_complex() -> complex:
    return -8.007 + 0.01j


@fixture(scope="module", autouse=True)
def alpha_complex() -> float:
    return -3.1 + 1j * pi / 4


@fixture(scope="module", autouse=True)
def omega() -> float:
    return 2.18


@fixture(scope="module", autouse=True)
def time_values(
    omega: float,
) -> float:
    return (2 * pi / omega) * np.linspace(start=-1, stop=2, endpoint=True, num=100)


@fixture(scope="function", autouse=True)
def intervals1() -> list[tuple[float, float]]:
    return [
        (-5, -3),
        (-0.4, -0.1),
        (0.2, 0.35),
        (0.8, 1.6),
    ]
