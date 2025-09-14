#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_euklidean_algorithm(
    test: TestCase,
):
    p = Poly.load_from_zeroes([1, 3, 3, 4, 5], lead=10)
    q = Poly.load_from_zeroes([-2, 3, 4, 7], lead=8)
    d, m, n = euklidean_algorithm(p, q, normalised=False)
    # check that d divides p, q
    test.assertEqual(p % d, 0)
    test.assertEqual(q % d, 0)
    # verify result
    d_ = m * p + n * q
    # NOTE: mathematically, all divisors of {p,q} divide d_,
    # Hence, if d == d_, then d is not only a divisor
    # but the maximal one upto similarity.
    np.testing.assert_array_almost_equal(d.coefficients, d_.coefficients)
    # this check is unnecessary, but do it anyway
    np.testing.assert_array_almost_equal(d.roots, [3, 4])
    return


def test_euklidean_algorithm_BOUNDARY_CASE1(
    test: TestCase,
):
    p = Poly.load_from_zeroes([1, 3, 3, 4, 5], lead=10)
    q = Poly.load_from_zeroes([1, 5], lead=8)
    d, _, _ = euklidean_algorithm(p, q, normalised=False)
    # check that d divides p, q
    test.assertEqual(p % d, 0)
    test.assertEqual(q % d, 0)
    # check that d ~ q
    test.assertEqual(d % q, 0)
    return
