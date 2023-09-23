#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.thirdparty.unit import *

from src.core.poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FIXTURES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@mark.parametrize(
    ('n', 'd', 't', 'cond'),
    [
        (0, 5, 0.0, [1, 0, 0, 0, 0, 0]),
        (0, 5, 0.1, [1, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5]),
        (0, 5, 1.0, [1, 1, 1, 1, 1, 1]),
        (2, 5, 0.0, [0, 0, 2 * 1 * 1, 0, 0, 0]),
        (2, 5, 1.0, [0, 0, 2 * 1, 3 * 2, 4 * 3, 5 * 4]),
        (2, 5, 0.1, [0, 0, 2 * 1 * 1, 3 * 2 * 1e-1, 4 * 3 * 1e-2, 5 * 4 * 1e-3]),
        (5, 5, 0.0, [0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]),
        (5, 5, 0.3, [0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]),
        (5, 5, 1.0, [0, 0, 0, 0, 0, 5 * 4 * 3 * 2 * 1]),
        (7, 5, 0.0, [0, 0, 0, 0, 0, 0]),
        (7, 5, 0.3, [0, 0, 0, 0, 0, 0]),
        (7, 5, 1.0, [0, 0, 0, 0, 0, 0]),
    ],
)
def test_force_poly_condition(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    n: int,
    d: int,
    t: float,
    cond: list[float],
):
    cond_ = force_poly_condition(n=n, d=d, t=t)
    C = (np.linalg.norm(cond) + np.linalg.norm(cond_)) / 2 or 1.0
    dist = np.linalg.norm(np.asarray(cond) - np.asarray(cond_))
    test.assertLess(dist, 1e-6 * C, f'{cond_} should equal {cond}')
    return


@mark.parametrize(
    ('d', 'opt', 'coeff'),
    [
        (
            3,
            [
                (0, 1.0),
            ],
            [-3, 1, 1, 1],
        ),
        (
            3,
            [
                (0, 0.0),
                (1, 1.0),
            ],
            [0, 6, 3, -4],
        ),
        (
            4,
            [
                (0, 0.0),
                (0, 1.0),
                (3, 1.0),
            ],
            [0, 7, -10, 4, -1],
        ),
    ],
)
def test_force_poly_conditions(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    d: int,
    opt: list[tuple[int, float]],
    coeff: list[float],
):
    A = force_poly_conditions(d=d, opt=opt)

    # these coefficients should satisfy all the conditions
    x = np.asarray(coeff)
    dist = np.linalg.norm(A @ x)
    test.assertLess(dist, 1e-6)

    # check onb
    Q = onb_conditions(d=d, opt=opt)
    m = Q.shape[1]
    for j in range(m):
        x = Q[:, j]
        dist = np.linalg.norm(A @ x)
        test.assertLess(dist, 1e-6)
    return
