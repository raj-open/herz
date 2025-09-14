#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Methods for eps-differences for aligned arrays.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from collections.abc import Iterable
from typing import TypeVar

import numpy as np
from numpy.typing import NDArray

from ...thirdparty.maths import *
from ..enums import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "normalised_diffs",
    "sign_normalised_diffs",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar("NUMBER", float, complex)

# ----------------------------------------------------------------
# METHODS - aligned arrays
# ----------------------------------------------------------------


def normalised_diffs(x_from: Iterable[NUMBER], x_to: Iterable[NUMBER]) -> NDArray[np.float64]:
    """
    Computes difference `x_to - x_from` relativised.

    Note:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.

    """
    x_from = np.asarray(x_from)
    x_to = np.asarray(x_to)
    dx = x_to - x_from
    C = np.maximum(1.0, (abs(x_from) + abs(x_to)) / 2)
    return dx / C


def sign_normalised_diffs(
    x_from: Iterable[NUMBER], x_to: Iterable[NUMBER], eps: float
) -> NDArray[np.float64]:
    r = normalised_diffs(x_from=x_from, x_to=x_to)
    check = np.full(r.shape, fill_value=EnumSign.NON_ZERO, dtype=EnumSign)

    cond_is_real = abs(r.imag) < eps
    cond_is_real_zero = cond_is_real & (abs(r.real) < eps)
    cond_sign_real = np.sign(r.real / eps)
    cond_is_real_nonzero = cond_is_real & ~cond_is_real_zero

    check[cond_is_real_nonzero & (cond_sign_real == 1)] = EnumSign.REAL_POSITIVE
    check[cond_is_real_nonzero & (cond_sign_real == -1)] = EnumSign.REAL_NEGATIVE
    check[cond_is_real_zero] = EnumSign.ZERO
    return check
