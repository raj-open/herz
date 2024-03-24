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
    values: Iterable[NUMBER],
    eps: float,
) -> list[NUMBER]:
    '''
    Cleans up values that are ε-close to being real-/imag-valued
    '''
    values = eps_clean_real(values, x=0, eps=eps)
    values = eps_clean_imag(values, x=0, eps=eps)
    return values


def eps_clean_boundaries(
    values: Iterable[NUMBER],
    eps: float,
    boundaries_real: tuple[float, float] = (-np.inf, np.inf),
    boundaries_imag: tuple[float, float] = (-np.inf, np.inf),
) -> list[NUMBER]:
    '''
    Clean up values that are ε-close to boundaries (treated box-like)
    '''
    for u in boundaries_real:
        if abs(u) < np.inf:
            values = eps_clean_real(values, x=u, eps=eps)

    for u in boundaries_imag:
        if abs(u) < np.inf:
            values = eps_clean_imag(values, x=u, eps=eps)

    return values


def eps_clean_real(
    values: Iterable[NUMBER],
    x: float,
    eps: float,
) -> list[complex]:
    '''
    Forces the real-part of values that are ε-close to a certain value, `x`, to be `x`.
    '''
    values = np.asarray(values, dtype=complex)
    d = sign_normalised_diff_matrix(x_from=[x], x_to=values.real, eps=eps)
    d = d.reshape(values.shape)
    values[d == EnumSign.ZERO] = x + 1j * values[d == EnumSign.ZERO].imag
    return values.tolist()


def eps_clean_imag(
    values: Iterable[NUMBER],
    x: float,
    eps: float,
) -> list[complex]:
    '''
    Forces the imag-part of values that are ε-close to a certain value, `x`, to be `x`.
    '''
    values = np.asarray(values, dtype=complex)
    d = sign_normalised_diff_matrix(x_from=[x], x_to=values.imag, eps=eps)
    d = d.reshape(values.shape)
    values[d == EnumSign.ZERO] = values[d == EnumSign.ZERO].real + 1j * x
    return values.tolist()
