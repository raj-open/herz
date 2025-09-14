#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import numpy as np

from tests.unit.thirdparty.unit import *

from src.models.enums import *
from src.models.polynomials import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("coeff", "t0", "period"),
    [
        ([1], 0, 1),
        ([0, 1], 0, 1),
        ([1, -3.1, 0.8], 0, 1),
        ([1], -0.2, 1),
        ([0, 1], -0.2, 1),
        ([1, -3.1, 0.8], -0.2, 1),
    ],
)
def test_resolve_piecewise_poly_CASES(
    test: TestCase,
    # fixtures
    intervals1: list[tuple[float, float]],
    C: float,
    # parameters
    coeff: list[float],
    t0: float,
    period: float,
):
    f = Poly[float](
        lead=C,
        coeff=coeff,
        cyclic=True,
        offset=t0,
        period=period,
    )
    for g, a, b in f.resolve_piecewise(*intervals1):
        test.assertFalse(g.cyclic, "new model should not be cyclic")
        times = np.linspace(start=a, stop=b, num=100, endpoint=False)
        times = times[a < times]
        np.testing.assert_array_almost_equal(
            g.values(times),
            f.values(times),
            err_msg='acyclic model should agree with cyclic model on "safe" interval',
        )
    return


@mark.parametrize(
    ("coeff", "t0", "period"),
    [
        ([1], 0, 1),
        ([0, 1], 0, 1),
        ([1, -3.1, 0.8], 0, 1),
        ([1], -0.2, 1),
        ([0, 1], -0.2, 1),
        ([1, -3.1, 0.8], -0.2, 1),
    ],
)
def test_resolve_piecewise_polyexp_CASES(
    test: TestCase,
    # fixtures
    intervals1: list[tuple[float, float]],
    alpha_complex: float,
    C_complex: complex,
    # parameters
    coeff: list[float],
    t0: float,
    period: float,
):
    f = PolyExp(
        alpha=alpha_complex,
        lead=C_complex,
        coeff=coeff,
        cyclic=True,
        offset=t0,
        period=period,
    )
    for g, a, b in f.resolve_piecewise(*intervals1):
        test.assertFalse(g.cyclic, "new model should not be cyclic")
        times = np.linspace(start=a, stop=b, num=100, endpoint=False)
        times = times[a < times]
        np.testing.assert_array_almost_equal(
            g.values(times),
            f.values(times),
            err_msg='acyclic model should agree with cyclic model on "safe" interval',
        )
    return
