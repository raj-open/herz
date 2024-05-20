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
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope='function')
def poly() -> Poly[float]:
    return Poly[float](coeff=[100, 3, 0, -0.7])


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
    ('deg', 'conds', 'coeff', 'T', 'intervals'),
    [
        (
            3,
            [
                PolyDerCondition(derivative=0, time=1.0),
            ],
            [-3, 1, 1, 1],
            1,
            [(0, 1)],
        ),
        (
            3,
            [
                PolyDerCondition(derivative=0, time=0.0),
                PolyDerCondition(derivative=1, time=1.0),
            ],
            [0, 6, 3, -4],
            1,
            [(0, 1)],
        ),
        (
            4,
            [
                PolyDerCondition(derivative=0, time=0.0),
                PolyDerCondition(derivative=0, time=1.0),
                PolyDerCondition(derivative=3, time=1.0),
            ],
            [0, 7, -10, 4, -1],
            1,
            [(0, 1)],
        ),
    ],
)
def test_force_poly_conditions(
    test: TestCase,
    # test parameters
    deg: int,
    conds: list[PolyDerCondition],
    coeff: list[float],
    T: float,
    intervals: Iterable[tuple[float, float]],
):
    A = force_poly_conditions(deg=deg, conds=conds)

    # these coefficients should satisfy all the conditions
    x = np.asarray(coeff)
    result = A @ x
    assert_array_close_to_zero(result)

    # check onb
    Q = onb_conditions(deg=deg, conds=conds, intervals=intervals)
    m = Q.shape[1]
    polys = [Poly(coeff=Q[:, j]) for j in range(m)]
    for i, f in enumerate(polys):
        for j, g in enumerate(polys):
            if j <= i:
                continue
            value = inner_product_poly_exp(f, g, *intervals)
            math.isclose(value, 0, rel_tol=1e-7)

    for j in range(m):
        x = Q[:, j]
        result = A @ x
        assert_array_close_to_zero(result)
    return


@mark.parametrize(
    ('deg', 'conds', 'T', 'intervals'),
    [
        (
            4,
            [
                PolyDerCondition(derivative=0, time=0.0),
                PolyDerCondition(derivative=0, time=1.0),
                PolyDerCondition(derivative=3, time=1.0),
            ],
            2,
            [(0.1, 0.3), (1, 1.5)],
        ),
    ],
)
def test_onb_spectrum(
    test: TestCase,
    poly: Poly[float],
    # test parameters
    deg: int,
    conds: list[PolyDerCondition],
    T: float,
    intervals: Iterable[tuple[float, float]],
):
    # compute onb
    Q = onb_conditions(deg=deg, conds=conds, intervals=intervals)

    # compute onb sprectrum for an example polynomial
    t = np.linspace(start=0, stop=T, num=1000, endpoint=False)
    x = poly.values(t)
    p = onb_spectrum(Q=Q, t=t, x=x, T=T, intervals=intervals, cyclic=False)

    # check that p = project of poly onto onb
    m = Q.shape[1]
    polys = [Poly[float](coeff=Q[:, j]) for j in range(m)]
    for q in polys:
        value1 = inner_product_poly_exp(poly, q, *intervals)
        value2 = inner_product_poly_exp(p, q, *intervals)
        math.isclose(value1, value2, rel_tol=1e-7)

    return
