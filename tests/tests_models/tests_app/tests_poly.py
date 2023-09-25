#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.thirdparty.unit import *

from src.core.poly import *
from src.models.app.poly import *
from src.models.app.poly import force_poly_condition
from src.models.app.poly import force_poly_conditions
from src.models.generated.app import *

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
    ('n', 'deg', 't', 'cond'),
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
    deg: int,
    t: float,
    cond: list[float],
):
    cond_ = force_poly_condition(deg=deg, cond=PolynomialCondition(derivative=n, time=t))
    C = (np.linalg.norm(cond) + np.linalg.norm(cond_)) / 2 or 1.0
    assert_arrays_close(cond, cond_, eps=1e-6)
    return


@mark.parametrize(
    ('deg', 'conds', 'coeff'),
    [
        (
            3,
            [
                PolynomialCondition(derivative=0, time=1.0),
            ],
            [-3, 1, 1, 1],
        ),
        (
            3,
            [
                PolynomialCondition(derivative=0, time=0.0),
                PolynomialCondition(derivative=1, time=1.0),
            ],
            [0, 6, 3, -4],
        ),
        (
            4,
            [
                PolynomialCondition(derivative=0, time=0.0),
                PolynomialCondition(derivative=0, time=1.0),
                PolynomialCondition(derivative=3, time=1.0),
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
    deg: int,
    conds: list[PolynomialCondition],
    coeff: list[float],
):
    A = force_poly_conditions(deg=deg, conds=conds)

    # these coefficients should satisfy all the conditions
    x = np.asarray(coeff)
    assert_array_close_to_zero(A @ x, eps=1e-6)

    # check onb
    Q = onb_conditions(deg=deg, conds=conds)
    m = Q.shape[1]
    for j in range(m):
        x = Q[:, j]
        assert_array_close_to_zero(A @ x, eps=1e-6)
    return
