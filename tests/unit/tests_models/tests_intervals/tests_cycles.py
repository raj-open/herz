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
    ('offset', 'period', 'intervals', 'expected'),
    [
        # basic
        (0, 1, [(0, 1)], [(0, 1)]),
    ],
)
def test_collapse_intervals_to_cycle_BASIC(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [
        (0, 1, [(5.1, 5.1)], []),
    ],
)
def test_collapse_intervals_to_cycle_EMPTY(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [
        (0, 1, [(2.6, 3.2)], [(0, 0.2), (0.6, 1)]),
    ],
)
def test_collapse_intervals_to_cycle_SPLITS(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals'),
    [
        (0, 1, [(0, 0.7), (3.6, 4)]),
        # first splits, then merges
        (0, 1, [(2.6, 4.2)]),
        (0.1, 1.3, [(2.6, 4.2)]),
    ],
)
def test_collapse_intervals_to_cycle_MERGE_WHOLE_CYCLE(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    assert np.isclose(result, [(offset, offset + period)], rtol=1e-7).all(), 'Expected full cycle to emerge.'
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [
        (0, 1, [(0.3, 0.5), (1.1, 1.4)], [(0.1, 0.5)]),
        (0, 1, [(-0.9, -0.6), (0.3, 0.5)], [(0.1, 0.5)]),
    ],
)
def test_collapse_intervals_to_cycle_MERGE_NOTTRIVIAL(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [
        (0, 1, [(0.3, 0.5), (1.7, 1.9)], [(0.3, 0.5), (0.7, 0.9)]),
        (0, 1, [(-0.3, -0.1), (0.3, 0.5)], [(0.3, 0.5), (0.7, 0.9)]),
    ],
)
def test_collapse_intervals_to_cycle_DISJOINT(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return


@mark.parametrize(
    ('offset', 'period', 'intervals', 'expected'),
    [(0.1, 2, [(4.4, 4.7), (6.5, 6.75), (-0.2, -0.15)], [(0.4, 0.75), (1.8, 1.85)])],
)
def test_collapse_intervals_to_cycle_MIXED(
    test: TestCase,
    # parameters
    offset: float,
    period: float,
    intervals: list[tuple[float, float]],
    expected: list[tuple[int, float, float]],
):
    results = collapse_intervals_to_cycle(intervals, offset=offset, period=period)
    result = np.asarray(results)
    expected = np.asarray(expected)
    assert np.isclose(result, expected, rtol=1e-7).all()
    return
