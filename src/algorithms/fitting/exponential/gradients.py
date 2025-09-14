#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np
from numpy.typing import NDArray

from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "inner_product_matrix",
    "inner_product_matrix_derivative",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def inner_product_matrix(
    ip: dict[set, float],
) -> NDArray[np.float64]:
    """
    Computes inner product matrix, useful for computing

    1. L²-loss function
    2. gradient of linear part of model.

    NOTE: mathematically, `G` is a positive matrix!
    (Verified numerically.)
    """
    return np.asarray(
        [
            [
                ip["1"],
                ip["exp"],
                ip["f"],
            ],
            [
                ip["exp"],
                ip["exp^2"],
                ip["f*exp"],
            ],
            [
                ip["f"],
                ip["f*exp"],
                ip["f^2"],
            ],
        ]
    )


def inner_product_matrix_derivative(
    ip: dict[set, float],
) -> NDArray[np.float64]:
    """
    Computes derivative of the inner product matrix wrt. β.
    """
    return np.asarray(
        [
            [
                0,
                ip["t*exp"],
                0,
            ],
            [
                ip["t*exp"],
                2 * ip["t*exp^2"],
                ip["t*f*exp"],
            ],
            [
                0,
                ip["t*f*exp"],
                0,
            ],
        ]
    )
