#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.models.intervals import *
from tests.unit.__paths__ import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

_module = get_module(__file__)

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ('offset', 'period', 'interval', 'expected'),
    [
        (0, 1, (0, 1), [(0, 0, 1)]),
        (0, 1, (-0.3, 0.5), [(-1, -0.3, 0), (0, 0, 0.5)]),
        (0.2, 1, (0, 1), [(-1, 0, 0.2), (0, 0.2, 1)]),
        (0.2, 0.5, (0, 1), [(-1, 0, 0.2), (0, 0.2, 0.7), (1, 0.7, 1)]),
        (0.2, 0.5, (0.2, 0.71), [(0, 0.2, 0.7), (1, 0.7, 0.71)]),
        (0.2, 0.5, (0.18, 0.7), [(-1, 0.18, 0.2), (0, 0.2, 0.7)]),
        (0.2, 0.5, (0.18, 0.71), [(-1, 0.18, 0.2), (0, 0.2, 0.7), (1, 0.7, 0.71)]),
        (0, 1, (5.1, 5.1), []),
    ],
)
def test_resolve_interval_CASES(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    interval: tuple[float, float],
    expected: list[tuple[int, float, float]],
):
    results = list(
        resolve_interval(
            offset=offset,
            period=period,
            interval=interval,
        )
    )
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [
        (0, 1, [(0, 0.3), (0.8, 1.1)], [(0, 0, 0.3), (0, 0.8, 1), (1, 1, 1.1)]),
    ],
)
def test_resolve_intervals_CASES(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = list(resolve_intervals(intervals, offset=offset, period=period))
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return
