#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'closest_index',
    'closest_indices',
    'closest_value',
    'closest_values',
    'is_epsilon_eq',
    'is_epsilon_lt',
    'is_epsilon_gt',
    'is_epsilon_le',
    'is_epsilon_ge',
    'are_epsilon_eq',
    'are_epsilon_lt',
    'are_epsilon_gt',
    'are_epsilon_le',
    'are_epsilon_ge',
    'normalised_difference',
    'normalised_diffs',
    'sign_normalised_difference',
    'sign_normalised_diffs',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

T = TypeVar('T')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - single values
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def is_epsilon_eq(arg1: float, arg2: float, eps: float) -> bool:
    return sign_normalised_difference(x_from=arg1, x_to=arg2, eps=eps) == 0


def is_epsilon_lt(arg1: float, arg2: float, eps: float) -> bool:
    return sign_normalised_difference(x_from=arg1, x_to=arg2, eps=eps) == 1


def is_epsilon_gt(arg1: float, arg2: float, eps: float) -> bool:
    return sign_normalised_difference(x_from=arg1, x_to=arg2, eps=eps) == -1


def is_epsilon_le(arg1: float, arg2: float, eps: float) -> bool:
    return not is_epsilon_gt(arg1, arg2, eps=eps)


def is_epsilon_ge(arg1: float, arg2: float, eps: float) -> bool:
    return not is_epsilon_lt(arg1, arg2, eps=eps)


def normalised_difference(x_from: float, x_to: float) -> float:
    '''
    Computes difference `x_to - x_from` relativised.

    NOTE:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.
    '''
    dx = x_to - x_from
    C = max(1.0, (abs(x_from) + abs(x_to)) / 2)
    return dx / C


def sign_normalised_difference(x_from: float, x_to: float, eps: float) -> Literal[0, -1, 1]:
    r = normalised_difference(x_from, x_to)
    if r > eps:
        return 1
    if r < -eps:
        return -1
    return 0


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - arrays
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def normalised_diffs(x_from: Iterable[float], x_to: Iterable[float]) -> np.ndarray:
    '''
    Computes difference `x_to - x_from` relativised.

    NOTE:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.
    '''
    x_from = np.asarray(x_from)
    x_to = np.asarray(x_to)
    dx = x_to - x_from
    C = np.maximum(1.0, (np.abs(x_from) + np.abs(x_to)) / 2)
    return dx / C


def sign_normalised_diffs(
    x_from: Iterable[float], x_to: Iterable[float], eps: float
) -> np.ndarray:
    r = normalised_diffs(x_from=x_from, x_to=x_to)
    check = np.zeros(shape=r.shape, dtype=int)
    check[r > eps] = 1
    check[r < -eps] = -1
    return check


def are_epsilon_eq(arg1: Iterable[float], arg2: Iterable[float], eps: float) -> bool:
    return sign_normalised_diffs(x_from=arg1, x_to=arg2, eps=eps) == 0


def are_epsilon_lt(arg1: Iterable[float], arg2: Iterable[float], eps: float) -> bool:
    return sign_normalised_diffs(x_from=arg1, x_to=arg2, eps=eps) == 1


def are_epsilon_gt(arg1: Iterable[float], arg2: Iterable[float], eps: float) -> bool:
    return sign_normalised_diffs(x_from=arg1, x_to=arg2, eps=eps) == -1


def are_epsilon_le(arg1: Iterable[float], arg2: Iterable[float], eps: float) -> bool:
    return ~are_epsilon_gt(arg1, arg2, eps=eps)


def are_epsilon_ge(arg1: Iterable[float], arg2: Iterable[float], eps: float) -> bool:
    return ~are_epsilon_lt(arg1, arg2, eps=eps)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - search
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def closest_index(x: float, points: Iterable[float], init: int = 0) -> int:
    try:
        dist = np.abs(np.asarray(points) - x)
        index = init + dist.argmin()
    except:
        raise ValueError('List of points must be non-empty!')
    return index


def closest_indices(
    X: Iterable[float],
    points: Iterable[float],
    init: int = 0,
) -> list[int]:
    indices = [closest_index(x, points, init=init) for x in X]
    return indices


def closest_value(x: float, points: Iterable[float]) -> T:
    i = closest_index(x, points)
    return points[i]


def closest_values(X: list[float], points: Iterable[float]) -> list[T]:
    indices = closest_indices(X, points)
    return [X[i] for i in indices]
