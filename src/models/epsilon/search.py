#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "closest_index",
    "closest_indices",
    "closest_value",
    "closest_values",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar("NUMBER", float, complex)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def closest_index(x: NUMBER, points: Iterable[NUMBER], init: int = 0) -> int:
    try:
        dist = abs(np.asarray(points) - x)
        index = init + dist.argmin()

    except Exception as _:
        raise ValueError("List of points must be non-empty!")

    return index


def closest_indices(
    X: Iterable[NUMBER],
    points: Iterable[NUMBER],
    init: int = 0,
) -> list[int]:
    indices = [closest_index(x, points, init=init) for x in X]
    return indices


def closest_value(x: NUMBER, points: Iterable[NUMBER]) -> NUMBER:
    i = closest_index(x, points)
    return points[i]


def closest_values(X: list[NUMBER], points: Iterable[NUMBER]) -> list[NUMBER]:
    indices = closest_indices(X, points)
    return [X[i] for i in indices]
