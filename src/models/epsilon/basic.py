#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import TypeVar

import numpy as np

from ...thirdparty.maths import *
from ..enums import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "is_epsilon_eq",
    "normalised_difference",
    "sign_normalised_difference",
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

NUMBER = TypeVar("NUMBER", float, complex)

# ----------------------------------------------------------------
# METHODS - single values
# ----------------------------------------------------------------


def is_epsilon_eq(arg1: NUMBER, arg2: NUMBER, eps: float) -> bool:
    return sign_normalised_difference(x_from=arg1, x_to=arg2, eps=eps) == EnumSign.ZERO


def normalised_difference(x_from: NUMBER, x_to: NUMBER) -> NUMBER:
    """
    Computes difference `x_to - x_from` relativised.

    Note:
    - For large numbers it is the same as a relative difference.
    - For small numbers this is the same as an ordinary difference.

    """
    dx = x_to - x_from
    C = max(1.0, (abs(x_from) + abs(x_to)) / 2)
    return dx / C


def sign_normalised_difference(x_from: NUMBER, x_to: NUMBER, eps: float) -> EnumSign:
    r = normalised_difference(x_from, x_to)
    ## FIXME: this does not work in unit-tests!
    # match abs(r.imag) < eps, abs(r.real) < eps, int(np.sign(r.real / eps)):
    #     # if imaginary part is non-zero, then cannot classify in terms of real value position
    #     case (False, _, _):
    #         return EnumSign.NON_ZERO
    #     case (True, False, 1):
    #         return EnumSign.REAL_POSITIVE
    #     case (True, False, -1):
    #         return EnumSign.REAL_NEGATIVE
    #     # case True, True, _:
    #     case _:
    #         return EnumSign.ZERO
    if abs(r.imag) >= eps:
        return EnumSign.NON_ZERO
    elif abs(r.real) < eps:
        return EnumSign.ZERO
    elif np.sign(r.real / eps) == 1:
        return EnumSign.REAL_POSITIVE
    else:
        return EnumSign.REAL_NEGATIVE
