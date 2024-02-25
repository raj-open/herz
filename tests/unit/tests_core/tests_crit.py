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
from src.core.crit import *

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


def test_get_critical_points(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
):
    # p(t) = t^2 - 2t + 1
    results = get_critical_points([1, -2, 1])
    test.assertEqual(len(results), 1)
    t0, y0, kinds = results[0]
    test.assertAlmostEqual(t0, 1.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.LOCAL_MINIMUM})

    # p(t) = -(t^2 - 2t + 1)
    results = get_critical_points([-1, 2, -1])
    test.assertEqual(len(results), 1)
    t0, y0, kinds = results[0]
    test.assertAlmostEqual(t0, 1)
    test.assertSetEqual(kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.LOCAL_MAXIMUM})

    # p(t) = t^3
    results = get_critical_points([0, 0, 0, 1])
    test.assertEqual(len(results), 1)
    t0, y0, kinds = results[0]
    test.assertAlmostEqual(t0, 0.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.ZERO, EnumCriticalPoints.INFLECTION})

    # Force
    #    p'(t) = t^2 - 3t + 2 = (t - 2)(t - 1)
    # => p''(t) = 2t - 3
    # so
    #    p''(1) = -1 --> (1, p(1)) loc. max
    #    p''(2) = +1 --> (2, p(2)) loc. min
    coeff = get_integral_coefficients([2, -3, 1])
    results = get_critical_points(coeff)
    test.assertEqual(len(results), 3)

    t0, y0, kinds = results[0]
    test.assertAlmostEqual(t0, 0.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.ZERO})

    t0, y0, kinds = results[1]
    test.assertAlmostEqual(t0, 1.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.LOCAL_MAXIMUM})

    t0, y0, kinds = results[2]
    test.assertAlmostEqual(t0, 2.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.LOCAL_MINIMUM})

    # Force
    #    p'(t) = t^2 - 2t + 1 = (t - 1)^2
    # => p''(t) = 2(t - 1)
    # => p'''(t) = 2
    # so
    #    p''(1) = 0
    #    p'''(1) > 0 --> (1, p(1)) inflection
    coeff = get_integral_coefficients([1, -2, 1])
    results = get_critical_points(coeff)
    test.assertEqual(len(results), 2)

    t0, y0, kinds = results[0]
    test.assertAlmostEqual(t0, 0.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.ZERO})

    t0, y0, kinds = results[1]
    test.assertAlmostEqual(t0, 1.0)
    test.assertSetEqual(kinds, {EnumCriticalPoints.INFLECTION})
    return
