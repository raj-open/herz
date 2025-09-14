#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


from math import pi

import numpy as np

from tests.unit.__paths__ import *
from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

_module = get_module(__file__)

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("s", "coeff"),
    itertools_product(
        [0, 1j, 2 * pi * 1j, -3],
        [
            [1],
            [0, 1],
            [0, 0, 1],
            [1, -2, 1],
            [3, 0.5, -0.8, 1.7],
        ],
    ),
)
def test_integral_poly_exp_ANALYTIC(
    test: TestCase,
    # test parameters
    s: complex,
    coeff: list[float],
):
    f = PolyExp(coeff=coeff, alpha=s)
    F = f.integral()
    f_ = F.derivative()
    test.assertEqual(f.alpha, f_.alpha)
    assert np.isclose(f.coefficients, f_.coefficients, rtol=1e-7).all()
    return


@mark.parametrize(
    ("tt", "s", "coeff"),
    itertools_product(
        [
            (0, 1),
            (3.1, 3.5),
        ],
        [0, 1j, 2 * pi * 1j, -3],
        [
            [1],
            [0, 1],
            [0, 0, 1],
            [1, -2, 1],
            [3, 0.5, -0.8, 1.7],
        ],
    ),
)
def test_integral_poly_exp_NUMERICAL(
    test: TestCase,
    # test parameters
    tt: tuple[int, int],
    s: complex,
    coeff: list[float],
):
    t1, t2 = tt
    f = PolyExp(coeff=coeff, alpha=s)
    # compute integral coefficients 'by hand':
    N = 10000
    t = np.linspace(start=t1, stop=t2, num=N, endpoint=False)
    dt = (t2 - t1) / N
    func_values = f.values(t)
    F_manual = sum(func_values) * dt

    # compute using method:
    F = f.integral()
    F_method = F.evaluate((t1, t2))

    # verify correctness of method:
    test.assertAlmostEqual(F_method, F_manual, delta=4)
    return
