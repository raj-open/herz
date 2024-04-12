#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.utils import *
from ..enums import *
from .basic_matrix import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'eps_clean_duplicates',
    'eps_clean_zeroes',
    'eps_clean_pure_real_imaginary',
    'eps_clean_boundaries',
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar('NUMBER', float, complex)

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def eps_clean_duplicates(
    values: list[NUMBER],
    eps: float,
) -> list[NUMBER]:
    if len(values) == 0:
        return []

    # --------------------------------
    # NOTE:
    # 1) Sort based on real part.
    # 2) Sorting of the imaginary part is not important.
    #    Just do this for efficiency.
    # --------------------------------
    values = sorted(values, key=lambda x: (x.real, x.imag))
    D = sign_normalised_diff_matrix(x_from=values, x_to=values, eps=eps)
    values_unique = []
    indices_ignore = []
    for i, value in enumerate(values):
        if i in indices_ignore:
            continue
        indices_ignore += characteristic_to_where(D[i, :] == EnumSign.ZERO)
        values_unique.append(value)

    return values_unique


def eps_clean_zeroes(
    values: Iterable[float],
    eps: float,
) -> list[float]:
    '''
    Cleans up values that are ε-close to being zero.
    '''
    return eps_clean_value(values, x=0, eps=eps)


def eps_clean_pure_real_imaginary(
    values: Iterable[complex],
    eps: float,
) -> list[complex]:
    '''
    Cleans up values that are ε-close to being zero.
    '''
    if not isinstance(values, np.ndarray):
        values = np.asarray(values)
    values = np.asarray(eps_clean_zeroes(values.real, eps=eps)) + 1j * np.asarray(
        eps_clean_zeroes(values.imag, eps=eps)
    )
    return values.tolist()


def eps_clean_boundaries(
    values: Iterable[float],
    eps: float,
    bounds: tuple[float, float] = (-np.inf, np.inf),
) -> list[float]:
    '''
    Clean up values that are ε-close to boundaries (treated box-like)
    '''
    for u in bounds:
        if abs(u) < np.inf:
            values = eps_clean_value(values, x=u, eps=eps)
    return values


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def eps_clean_value(
    values: Iterable[float],
    x: float,
    eps: float,
) -> list[float]:
    '''
    Forces the real-part of values that are ε-close to a certain value, `x`, to be `x`.
    '''
    values = np.asarray(values)
    values.flags.writeable = True  # DEV-NOTE: this is sometimes necessary
    d = sign_normalised_diff_matrix(x_from=[x], x_to=values, eps=eps)
    d = d.reshape(values.shape)
    values[d == EnumSign.ZERO] = x
    return values.tolist()
