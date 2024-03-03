#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.enums import *
from src.core.poly import *

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
    ('coeff', 't0', 'coeff_r'),
    [
        ([1], 0.3, [1]),
        ([1, 1], 0.3, [1 + 0.3, 1]),
        ([1, -2, 1], 1, [0, 0, 1]),
        ([1, 2, 1], -1, [0, 0, 1]),
    ],
)
def test_get_recentred_coefficients_rote(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    coeff: list[float],
    t0: float,
    coeff_r: list[float],
):
    coeff_r_ = get_recentred_coefficients(coeff, t0)
    np.testing.assert_array_almost_equal(coeff_r_, coeff_r, decimal=6)
    return


def test_get_real_polynomial_roots(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
):
    coeff = [-3, 0, 8, 1]
    roots = get_real_polynomial_roots(coeff)
    assert_array_close_to_zero(
        [poly_single(t, *coeff) for t in roots],
        eps=1e-10,
        message='The values computes should be roots of the polynomial.',
    )

    roots = get_real_polynomial_roots([0, 0, -4, 1])
    np.testing.assert_array_equal(
        roots,
        [0, 0, 4],
        'Roots of algebric multiplicity should occur repeated in list.',
    )

    roots = get_real_polynomial_roots([0, 0, 0, -4, 1])
    np.testing.assert_array_equal(
        roots,
        [0, 0, 0, 4],
        'Roots of algebric multiplicity should occur repeated in list.',
    )
    return


@mark.parametrize(
    ('coeff', 'zeroes'),
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
        (
            [0, 0, 1],
            [0, 0],
        ),
    ],
)
def test_get_real_polynomial_roots_rote(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    coeff: list[float],
    zeroes: list[float],
):
    roots = get_real_polynomial_roots(coeff)
    np.testing.assert_array_almost_equal(roots, zeroes, decimal=6)
    return


def test_get_derivative_coefficients(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
):
    coeff = get_derivative_coefficients([0, 1, 1])
    np.testing.assert_array_equal(coeff, [1, 2])
    return


@mark.parametrize(
    ('coeff', 'n', 'expected'),
    [
        ([4, 5, 6, -10], 0, [4, 5, 6, -10]),
        ([4, 5, 6, -10], 1, [5, 6 * 2, -10 * 3]),
        ([4, 5, 6, -10], 2, [6 * 2, -10 * 3 * 2]),
        ([4, 5, 6, -10], 3, [-10 * 3 * 2]),
    ],
)
def test_get_derivative_coefficients_rote(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    coeff: list[float],
    n: int,
    expected: list[float],
):
    coeff_ = get_derivative_coefficients(coeff, n=n)
    np.testing.assert_array_almost_equal(coeff_, expected, decimal=6)
    return


def test_get_integral_coefficients(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
):
    coeff = get_integral_coefficients([1, 2])
    np.testing.assert_array_equal(coeff, [0, 1, 1])

    coeff = get_derivative_coefficients(coeff)
    np.testing.assert_array_equal(coeff, [1, 2], 'Derivative should return original coefficients.')
    return


@mark.parametrize(
    ('coeff', 'n', 'expected'),
    [
        ([4, 5, 6, -10], 0, [4, 5, 6, -10]),
        ([4, 5, 6, -10], 1, [0, 4, 5 / 2, 6 / 3, -10 / 4]),
        ([4, 5, 6, -10], 2, [0, 0, 4 / 2, 5 / (2 * 3), 6 / (3 * 4), -10 / (4 * 5)]),
        (
            [4, 5, 6, -10],
            3,
            [0, 0, 0, 4 / (2 * 3), 5 / (2 * 3 * 4), 6 / (3 * 4 * 5), -10 / (4 * 5 * 6)],
        ),
    ],
)
def test_get_integral_coefficients_rote(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    coeff: list[float],
    n: int,
    expected: list[float],
):
    coeff_ = get_integral_coefficients(coeff, n=n)
    np.testing.assert_array_almost_equal(coeff_, expected, decimal=6)

    coeff_ = get_derivative_coefficients(expected, n=n)
    np.testing.assert_array_almost_equal(
        coeff_,
        coeff,
        decimal=6,
        err_msg='Derivative should return original coefficients.',
    )
    return
