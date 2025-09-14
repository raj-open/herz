#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.thirdparty.unit import *

from src.models.polynomials import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("coeff_p", "coeff_q", "coeff_result"),
    [
        ([1, 1], [1], [1, 1]),
        ([0, 6, 0, 16], [0, 2], [3, 0, 8]),
        ([100, 6, 0, 16], [0, 2], [3, 0, 8]),
    ],
)
def test_get_long_division_CASES(
    test: TestCase,
    # test parameters
    coeff_p: list[float],
    coeff_q: list[float],
    coeff_result: list[float],
):
    p = Poly(coeff=coeff_p)
    q = Poly(coeff=coeff_q)
    result = Poly(coeff=coeff_result)
    test.assertEqual(p // q, result)
    return


@mark.parametrize(
    ("coeff_p", "coeff_q"),
    [
        ([1], [1, 1]),
        ([0, 2], [100, 6, 0, 16]),
    ],
)
def test_get_long_division_ZERO_DIVISION(
    test: TestCase,
    # test parameters
    coeff_p: list[float],
    coeff_q: list[float],
):
    p = Poly(coeff=coeff_p)
    q = Poly(coeff=coeff_q)
    test.assertEqual(p // q, 0)
    return


@mark.parametrize(
    ("coeff_p", "coeff_q", "coeff_result"),
    [
        ([100, 6, 0, 16], [0, 2], [100]),
        ([100, 6, 0, 16], [1, 2], [95]),
    ],
)
def test_get_modulo_CASES(
    test: TestCase,
    # test parameters
    coeff_p: list[float],
    coeff_q: list[float],
    coeff_result: list[float],
):
    p = Poly(coeff=coeff_p)
    q = Poly(coeff=coeff_q)
    result = Poly(coeff=coeff_result)
    test.assertEqual(p % q, result)
    return


@mark.parametrize(
    ("coeff_p", "coeff_q"),
    [
        ([0, 2], [100, 6, 0, 16]),
        ([1, 2, -3], [100, 6, 0, 16]),
    ],
)
def test_get_modulo_TRIVIAL(
    test: TestCase,
    # test parameters
    coeff_p: list[float],
    coeff_q: list[float],
):
    p = Poly(coeff=coeff_p)
    q = Poly(coeff=coeff_q)
    test.assertEqual(p % q, p)
    return


@mark.parametrize(
    ("coeff_p", "coeff_q"),
    [
        ([0, 0, 100], [100]),
        ([0, 0, 1, 2, -0.3], [1, 2, -0.3]),
        ([21, -10, 1], [-3, 1]),
        ([21, -10, 1], [-6, 2]),
    ],
)
def test_get_long_division_ZERO_REST(
    test: TestCase,
    # test parameters
    coeff_p: list[float],
    coeff_q: list[float],
):
    p = Poly(coeff=coeff_p)
    q = Poly(coeff=coeff_q)
    test.assertEqual(p % q, 0)
    return
