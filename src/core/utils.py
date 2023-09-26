#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from .constants import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'flatten',
    'relative_change',
    'signed_relative_change',
    'where_to_characteristic',
    'characteristic_to_where',
    'normalise_to_unit_interval',
    'integral_interpolated',
    'innerproduct_interpolated',
    'norm_interpolated',
    'normalise_interpolated',
    'normalise_interpolated_drift',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

T = TypeVar('T')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - INDICES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def where_to_characteristic(indices: list[int] | np.ndarray, N: int) -> list[bool]:
    X = np.asarray([False] * N)
    X[indices] = True
    return X.tolist()


def characteristic_to_where(ch: list[bool] | np.ndarray) -> list[int]:
    obj = np.where(ch)
    return obj[0].tolist()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - ARRAYS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def flatten(*X: list[T]) -> list[T]:
    return list(itertools_chain(*X))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - COMPARISONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def relative_change(x1: float, x2: float) -> float:
    C = (np.abs(x1) + np.abs(x2)) / 2
    return (x2 - x1) / (C or 1.0)


def signed_relative_change(x1: float, x2: float, eps: MACHINE_EPS) -> Literal[0, -1, 1]:
    r = relative_change(x1, x2)
    if r > eps:
        return 1
    if r < -eps:
        return -1
    return 0


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - MATHS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def normalise_to_unit_interval(t: np.ndarray) -> tuple[np.ndarray, float]:
    t_min = min(t)
    t_max = max(t)
    T = t_max - t_min
    t = (t - t_min) / (T or 1.0)
    return t, T


def integral_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = False,
) -> float:
    '''
    Computes integral based on piecewise linear interpolation
    of a discrete time-series (`t`, `x`)
    '''
    t = np.asarray(t.tolist() + [T])

    if periodic:
        x = np.asarray(x.tolist() + [x[0]])
    else:
        x1 = np.asarray(x[1:])
        x2 = np.asarray(x[:-1])
        x = np.concatenate([[x[0]], (x1 + x2) / 2, [x[-1]]])

    dt = np.diff(t)
    x_m = (x[:-1] + x[1:]) / 2
    I = sum(x_m * dt)
    if average:
        I = I / T
    return I


def innerproduct_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = integral_interpolated(t, x * y, T=T, periodic=periodic, average=average)
    return s


def norm_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
    periodic: bool = False,
    average: bool = True,
) -> float:
    s = innerproduct_interpolated(t, x, x, T=T, periodic=periodic, average=average)
    return np.sqrt(s)


def normalise_interpolated(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
) -> tuple[float, float, np.ndarray]:
    m = integral_interpolated(t, x, T=T, periodic=False, average=True)
    x = x - m * (t - t[0])
    s = norm_interpolated(t, x, T=T, periodic=False, average=True)
    x = x / (s or 1.0)
    return m, s, x


def normalise_interpolated_drift(
    t: np.ndarray,
    x: np.ndarray,
    T: float,
) -> tuple[float, float, float, np.ndarray]:
    m = (x[-1] - x[0]) / (t[-1] - t[0])
    c = x[0] - m * t[0]
    x = x - (c + m * t)
    s = norm_interpolated(t, x, T=T, periodic=False, average=True)
    x = x / (s or 1.0)
    return c, m, s, x
