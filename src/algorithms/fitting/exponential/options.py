#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.types import *
from ....thirdparty.maths import *

from .geometry import *
from .gradients import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fit_options_scale_data',
    'fit_options_gradients_data',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_options_scale_data(
    data: NDArray[np.float64],
) -> float:
    '''
    Determines the L²-norm of the data curves.
    Useful for scaling the loss function and errors.
    '''
    t, dt, x = data[:, 0], data[:, 1], data[:, -1]
    T = max(t) - min(t) + np.mean(dt)
    norm_x = math.sqrt(np.sum((x**2) * dt) / T)
    return norm_x


def fit_options_gradients_data(
    data: NDArray[np.float64],
) -> Callable[[float], tuple[NDArray[np.float64], NDArray[np.float64]]]:

    def method(x: NDArray[np.float64]):
        beta = x[-1]
        ip = compute_inner_products_from_data(data=data, beta=beta)
        G = inner_product_matrix(ip)
        DG = inner_product_matrix_derivative(ip)
        return G, DG

    return method
