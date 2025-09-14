#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.thirdparty.unit import *

from src.algorithms.jordan import *
from src.models.polynomials import *
from src.thirdparty.maths import *
from src.thirdparty.types import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_characteristic_polynomial(
    test: TestCase,
    # fixtures
    random_jordan_small: NDArray[np.float64],
):
    A = random_jordan_small
    p = characteristic_polynomial(A)
    Apow = np.eye(*A.shape)
    pA = np.zeros(A.shape)
    for k, a in enumerate(p.coefficients):
        if k > 0:
            Apow = Apow @ A
        pA += a * Apow
    test.assertAlmostEqual(np.linalg.norm(pA), 0, msg="char(A) should be the 0-matrix")
    return


def test_chinese_polynomial(
    test: TestCase,
):
    data: list[tuple[float, Poly[float]]] = [
        (2, Poly[float](coeff=[-2, 1]) ** 3),
        (5, Poly[float](coeff=[-5, 1]) ** 2),
    ]
    ch = chinese_polynomial(data)
    for t, q in data:
        rest = ch % q
        test.assertEqual(rest.degree, 0)
        test.assertAlmostEqual(rest.coefficients[0], t, msg="expected ch % q to be a scalar")
    return
