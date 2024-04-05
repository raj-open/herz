#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.polynomials import *
from src.algorithms.jordan import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_chevalley_polynomial(
    test: TestCase,
    # fixtures
    random_jordan_small: NDArray[np.float64],
):
    A = random_jordan_small
    stats = algebraic_dimensions(A)
    ch = chevalley_polynomial(A)
    for t, n in stats.items():
        q = Poly(coeff=[-t, 1]) ** n
        rest = ch % q
        test.assertEqual(rest.degree, 0, msg='expected ch % q to be a scalar')
        test.assertAlmostEqual(rest.coefficients[0], t, msg='expected ch % (X - t)^n = t')
    return


def test_compute_decomposition_SMALL_CASE(
    test: TestCase,
    # fixtures
    random_jordan_small: NDArray[np.float64],
):
    A = random_jordan_small
    (V, Vinv), (D, N) = decompose_jordan_chevalley(A)
    np.testing.assert_array_almost_equal(D, np.diag(np.diag(D)), err_msg='D should be diagonal')
    np.testing.assert_array_almost_equal(np.diag(np.diag(N)), np.zeros(N.shape), err_msg='N should be offdiagonal')
    np.testing.assert_array_almost_equal(D @ N, N @ D, err_msg='decomposition should consist of commuting matrices')
    np.testing.assert_array_almost_equal(
        V @ (D + N) @ Vinv, A, err_msg='decomposition should reconstruct the original matrix'
    )
    return


def test_compute_decomposition_GRAPH_CASE(
    test: TestCase,
    # fixtures
    weights: NDArray[np.float64],
    generator: NDArray[np.float64],
):
    A = generator
    (V, Vinv), (D, N) = decompose_jordan_chevalley(A)
    np.testing.assert_array_almost_equal(D, np.diag(np.diag(D)), err_msg='D should be diagonal')
    np.testing.assert_array_almost_equal(np.diag(np.diag(N)), np.zeros(N.shape), err_msg='N should be offdiagonal')
    np.testing.assert_array_almost_equal(D @ N, N @ D, err_msg='decomposition should consist of commuting matrices')
    np.testing.assert_array_almost_equal(
        V @ (D + N) @ Vinv, A, err_msg='decomposition should reconstruct the original matrix'
    )
    return
