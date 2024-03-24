#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from src.algorithms.fitting.polynomials import *

from src.models.fitting import *
from src.algorithms.fitting.polynomials.geometry import *

# private method
from src.algorithms.fitting.polynomials.geometry import force_poly_conditions

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ('n', 'deg', 't', 'expected'),
    [
        (0, 5, 0.0, [[1, 0, 0, 0, 0, 0]]),
        (0, 5, 0.1, [[1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5]]),
        (0, 5, 1.0, [[1, 1, 1, 1, 1, 1]]),
        (2, 5, 0.0, [[0, 0, 2 * 1 * 1, 0, 0, 0]]),
        (2, 5, 1.0, [[0, 0, 2 * 1, 3 * 2, 4 * 3, 5 * 4]]),
        (2, 5, 0.1, [[0, 0, 2 * 1 * 1, 3 * 2 * 1e-1, 4 * 3 * 1e-2, 5 * 4 * 1e-3]]),
        (5, 5, 0.0, [[0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]]),
        (5, 5, 0.3, [[0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]]),
        (5, 5, 1.0, [[0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]]),
        (7, 5, 0.0, [[0, 0, 0, 0, 0, 0]]),
        (7, 5, 0.3, [[0, 0, 0, 0, 0, 0]]),
        (7, 5, 1.0, [[0, 0, 0, 0, 0, 0]]),
    ],
)
def test_force_poly_conditions(
    test: TestCase,
    # test parameters
    n: int,
    deg: int,
    t: float,
    expected: list[list[float]],
):
    cond = force_poly_conditions(deg=deg, conds=[PolyDerCondition(derivative=n, time=t)])
    np.testing.assert_array_almost_equal(cond, expected, decimal=6)
    return


@mark.parametrize(
    ('deg', 'conds', 'coeff'),
    [
        (
            3,
            [
                PolyDerCondition(derivative=0, time=1.0),
            ],
            [-3, 1, 1, 1],
        ),
        (
            3,
            [
                PolyDerCondition(derivative=0, time=0.0),
                PolyDerCondition(derivative=1, time=1.0),
            ],
            [0, 6, 3, -4],
        ),
        (
            4,
            [
                PolyDerCondition(derivative=0, time=0.0),
                PolyDerCondition(derivative=0, time=1.0),
                PolyDerCondition(derivative=3, time=1.0),
            ],
            [0, 7, -10, 4, -1],
        ),
    ],
)
def test_force_poly_conditions(
    test: TestCase,
    # test parameters
    deg: int,
    conds: list[PolyDerCondition],
    coeff: list[float],
):
    A = force_poly_conditions(deg=deg, conds=conds)

    # these coefficients should satisfy all the conditions
    x = np.asarray(coeff)
    result = A @ x
    assert_array_close_to_zero(result)

    # check onb
    t1 = 0
    t2 = 1
    Q = onb_conditions(deg=deg, conds=conds, t1=t1, t2=t2)
    m = Q.shape[1]
    polys = [Poly(coeff=Q[:, j]) for j in range(m)]
    for i, f in enumerate(polys):
        for j, g in enumerate(polys):
            if j <= i:
                continue
            value = inner_product_poly_exp(f, g, (t1, t2))
            np.testing.assert_almost_equal(value, 0)

    for j in range(m):
        x = Q[:, j]
        result = A @ x
        assert_array_close_to_zero(result)
    return
