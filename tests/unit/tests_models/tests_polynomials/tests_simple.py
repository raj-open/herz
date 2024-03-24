#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.enums import *
from src.models.polynomials import *

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
def test_get_recentred_coefficients_CASES(
    test: TestCase,
    # test parameters
    coeff: list[float],
    t0: float,
    coeff_r: list[float],
):
    p = Poly(coeff=coeff)
    p_recentred = p.rescale(t0=t0)
    np.testing.assert_array_almost_equal(p_recentred.coefficients, coeff_r)
    return


def test_real_polynomial_roots(
    test: TestCase,
):
    p = Poly(coeff=[-3, 0, 8, 1])
    roots = p.real_roots
    assert_array_close_to_zero(
        [p(t) for t in roots],
        message='The values computes should be roots of the polynomial.',
    )

    p = Poly(coeff=[0, 0, -4, 1])
    roots = p.real_roots
    np.testing.assert_array_equal(
        roots,
        [0, 0, 4],
        'Roots of algebric multiplicity should occur repeated in list.',
    )

    p = Poly(coeff=[0, 0, 0, -4, 1])
    roots = p.real_roots
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
def test_real_polynomial_roots_CASES(
    test: TestCase,
    # test parameters
    coeff: list[float],
    zeroes: list[float],
):
    p = Poly(coeff=coeff)
    roots = p.real_roots
    np.testing.assert_array_almost_equal(roots, zeroes, decimal=6)
    return


def test_derivative_coefficients(
    test: TestCase,
):
    p = Poly(coeff=[0, 1, 1])
    p = p.derivative()
    coeff = p.coefficients
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
def test_derivative_coefficients_CASES(
    test: TestCase,
    # test parameters
    coeff: list[float],
    n: int,
    expected: list[float],
):
    p = Poly(coeff=coeff)
    q = p.derivative(n)
    np.testing.assert_array_almost_equal(q.coefficients, expected)
    return


def test_integral_coefficients(
    test: TestCase,
):
    p = Poly(coeff=[1, 2])
    q = p.integral()
    np.testing.assert_array_equal(q.coefficients, [0, 1, 1])

    p_ = q.derivative()
    np.testing.assert_array_equal(p_.coefficients, [1, 2], 'Derivative should return original coefficients.')
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
def test_integral_coefficients_CASES(
    test: TestCase,
    # test parameters
    coeff: list[float],
    n: int,
    expected: list[float],
):
    p = Poly(coeff=coeff)
    q = p.integral(n)
    np.testing.assert_array_almost_equal(q.coefficients, expected)

    p_ = q.derivative(n)
    np.testing.assert_array_almost_equal(
        p_.coefficients,
        coeff,
        err_msg='Derivative should return original coefficients.',
    )
    return
