#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.core.constants import *
from src.models.critical import *
from src.models.polynomials import *
from src.algorithms.critical import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_get_critical_points(
    test: TestCase,
    # fixtures
    eps: float,
):
    # p(t) = t^2 - 2t + 1
    p = Poly(coeff=[1, -2, 1])
    results = get_critical_points(p, p.derivative())
    [results] = clean_up_critical_points([results], eps=eps, real_valued=True)
    test.assertEqual(len(results), 1)
    pt = results[0]
    test.assertAlmostEqual(pt.x, 1.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.LOCAL_MINIMUM})

    # p(t) = -(t^2 - 2t + 1)
    p = Poly(coeff=[-1, 2, -1])
    results = get_critical_points(p, p.derivative())
    [results] = clean_up_critical_points([results], eps=eps, real_valued=True)
    test.assertEqual(len(results), 1)
    pt = results[0]
    test.assertAlmostEqual(pt.x, 1)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.LOCAL_MAXIMUM})

    # p(t) = t^3
    p = Poly(coeff=[0, 0, 0, 1])
    results = get_critical_points(p, p.derivative())
    [results] = clean_up_critical_points([results], eps=eps, real_valued=True)
    test.assertEqual(len(results), 1)
    pt = results[0]
    test.assertAlmostEqual(pt.x, 0.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.INFLECTION})

    # Force
    #    p'(t) = t^2 - 3t + 2 = (t - 2)(t - 1)
    # => p''(t) = 2t - 3
    # so
    #    p''(1) = -1 --> (1, p(1)) loc. max
    #    p''(2) = +1 --> (2, p(2)) loc. min
    p = Poly(coeff=[2, -3, 1])
    q = p.integral()
    results = get_critical_points(q, q.derivative())
    [results] = clean_up_critical_points([results], eps=eps, real_valued=True)
    test.assertEqual(len(results), 3)

    pt = results[0]
    test.assertAlmostEqual(pt.x, 0.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.ZERO})

    pt = results[1]
    test.assertAlmostEqual(pt.x, 1.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.LOCAL_MAXIMUM})

    pt = results[2]
    test.assertAlmostEqual(pt.x, 2.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.LOCAL_MINIMUM})

    # Force
    #    p'(t) = t^2 - 2t + 1 = (t - 1)^2
    # => p''(t) = 2(t - 1)
    # => p'''(t) = 2
    # so
    #    p''(1) = 0
    #    p'''(1) > 0 --> (1, p(1)) inflection
    p = Poly(coeff=[1, -2, 1])
    q = p.integral()
    results = get_critical_points(q, q.derivative())
    [results] = clean_up_critical_points([results], eps=eps, real_valued=True)
    test.assertEqual(len(results), 2)

    pt = results[0]
    test.assertAlmostEqual(pt.x, 0.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.ZERO})

    pt = results[1]
    test.assertAlmostEqual(pt.x, 1.0)
    test.assertSetEqual(pt.kinds, {EnumCriticalPoints.INFLECTION})
    return
