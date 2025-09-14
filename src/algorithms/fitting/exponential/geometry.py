#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np
from numpy.typing import NDArray

from ....models.polynomials import *
from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "compute_inner_products_from_data",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def compute_inner_products_from_data(
    data: NDArray[np.float64],
    beta: float,
) -> dict[set, float]:
    """
    Model is

    y = A + B·exp(βx)

    Thus need inner products in order to compute
    L²-loss function + gradients.
    """
    dt, x, y = data[:, 1], data[:, 2], data[:, -1]
    ones = np.ones(x.shape)
    E = np.exp(beta * x)
    E2 = E**2
    y2 = y**2

    return {
        "1": np.sum(ones * dt),
        "exp": np.sum(E * dt),
        "exp^2": np.sum(E2 * dt),
        "f": np.sum(y * dt),
        "f*exp": np.sum((y * E) * dt),
        "f^2": np.sum(y2 * dt),
        "t*exp": np.sum((x * E) * dt),
        "t*exp^2": np.sum((x * E2) * dt),
        "t*f*exp": np.sum((x * y * E) * dt),
    }
