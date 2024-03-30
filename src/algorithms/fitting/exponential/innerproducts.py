#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....models.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'compute_inner_products_from_data',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def compute_inner_products_from_data(
    data: NDArray[np.float64],
    beta: float,
) -> dict[set, float]:
    '''
    Model is

    y = A + B·exp(βx)

    Thus need inner products in order to compute
    L²-loss function + gradients.
    '''
    t, dt, x = data[:, 0], data[:, 1], data[:, 2]
    E = np.exp(beta * t)
    E2 = np.exp(2 * beta * t)

    return {
        '1': np.sum(dt),
        'exp': np.sum(E * dt),
        'exp^2': np.sum(E2 * dt),
        'f': np.sum(x * dt),
        'f*exp': np.sum((x * E) * dt),
        'f^2': np.sum((x**2) * dt),
        't*exp': np.sum(t * E * dt),
        't*exp^2': np.sum(t * E2 * dt),
        't*f*exp': np.sum(t * x * E * dt),
    }
