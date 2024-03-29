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
    ('intervals', 'expected'),
    [
        (
            [
                (0, 1),
                (2, 3),
            ],
            [
                frozenset({0}),
                frozenset({1}),
            ],
        ),
        (
            [
                (0, 1),
                (1, 2),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                (0, 1),
                (-1, 0),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                (0, 1),
                (-0.1, 1.2),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                (0, 1),
                (0.2, 0.9),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                (0, 1),
                (-0.1, 0.5),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                (0, 1),
                (0.5, 1.2),
            ],
            [
                frozenset({0, 1}),
            ],
        ),
        (
            [
                ## component 0
                (0, 1),
                (0.8, 3),
                (2, 4),
                ## component 1
                (5, 6),
                ## component 0
                (4, 4.1),
                (-0.2, 0.5),
                ## component 1
                (5.5, 7),
                ## component 2
                (8, 9),
            ],
            [
                frozenset({0, 1, 2, 4, 5}),
                frozenset({3, 6}),
                frozenset({7}),
            ],
        ),
    ],
)
def test_compute_overlaps_BASIC(
    test: TestCase,
    # parameters
    intervals: list[tuple[float, float]],
    expected: list[set[int]],
):
    conn = list(compute_overlaps(intervals))
    test.assertSetEqual(set(conn), set(expected))
    return


@mark.parametrize(
    ('intervals', 'expected'),
    [
        (
            [
                ## component 0
                (0, 1),
                (0.8, 3),
                (2, 4),
                ## component 1
                (5, 6),
                ## component 0
                (4, 4.1),
                (-0.2, 0.5),
                ## component 1
                (5.5, 7),
                ## component 2
                (8, 9),
            ],
            [
                frozenset({0, 1, 2, 4, 5}),
                frozenset({3, 6}),
                frozenset({7}),
            ],
        ),
    ],
)
def test_resolve_interval_TRANSITIVITY(
    test: TestCase,
    # parameters
    intervals: list[tuple[float, float]],
    expected: list[set[int]],
):
    conn = list(compute_overlaps(intervals))
    test.assertSetEqual(set(conn), set(expected))
    return


@mark.parametrize(
    ('intervals', 'expected'),
    [
        (
            [
                ## component 0
                (0, 1),
                (0.8, 3),
                (2, 4),
                ## component 1
                (5, 6),
                ## component 0
                (4, 4.1),
                (-0.2, 0.5),
                ## component 1
                (5.5, 7),
                ## component 2
                (8, 9),
                # no component
                (10, 10),
            ],
            [
                (-0.2, 4.1),
                (5, 7),
                (8, 9),
            ],
        ),
    ],
)
def test_merge_intervals_TRANSIVITIY(
    test: TestCase,
    # parameters
    intervals: list[tuple[float, float]],
    expected: list[set[int]],
):
    results = list(merge_intervals(intervals))
    test.assertSetEqual(set(results), set(expected))
    return
