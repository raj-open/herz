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
    ('coeffs', 'zeroes'),
    [
        (
            [2, 1],
            [-2],
        ),
        (
            [1, 2],
            [-0.5],
        ),
        (
            [1, 0, 1],
            [],
        ),
        (
            [-1, 0, 1],
            [-1, 1],
        ),
        (
            [0, 1],
            [0],
        ),
    ],
)
def test_get_real_polynomial_roots(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    coeffs: list[float],
    zeroes: list[float],
):
    roots = get_real_polynomial_roots(*coeffs)
    roots = sorted(roots)
    zeroes = sorted(zeroes)
    dist = np.linalg.norm(np.asarray(roots) - np.asarray(zeroes))
    test.assertLess(dist, 1e-6)
    return
