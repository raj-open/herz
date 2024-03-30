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
    'inner_product_matrix',
    'inner_product_matrix_derivative',
    'loss_function',
    'loss_function_gradient',
    'solve_linear_part',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def inner_product_matrix(
    ip: dict[set, float],
) -> NDArray[np.float64]:
    '''
    Computes inner product matrix, useful for computing

    1. L²-loss function
    2. gradient of linear part of model.

    NOTE: mathematically, `G` is a positive matrix!
    (Verified numerically.)
    '''
    return np.asarray(
        [
            [
                ip['1'],
                ip['exp'],
                ip['f'],
            ],
            [
                ip['exp'],
                ip['exp^2'],
                ip['f*exp'],
            ],
            [
                ip['f'],
                ip['f*exp'],
                ip['f^2'],
            ],
        ]
    )


def inner_product_matrix_derivative(
    ip: dict[set, float],
) -> NDArray[np.float64]:
    '''
    Computes derivative of the inner product matrix wrt. β.
    '''
    return np.asarray(
        [
            [
                0,
                ip['t*exp'],
                0,
            ],
            [
                ip['t*exp'],
                2 * ip['t*exp^2'],
                ip['t*f*exp'],
            ],
            [
                0,
                ip['t*f*exp'],
                0,
            ],
        ]
    )


# ----------------------------------------------------------------
# METHODS - LOSS FUNCTION
# ----------------------------------------------------------------


def loss_function(
    G: NDArray[np.float64],
    x: NDArray[np.float64],
) -> float:
    '''
    We have
    ```
    loss := ½‖f - p‖²
    = ½⟨f - p, f - p⟩
    = ½⟨y, Gy⟩
    ```
    where
    ```
    y[:-1] = x[:-1]
    y[-1] = -1
    ```
    '''
    y = x.copy()
    y[-1] = -1
    loss = np.inner(G @ y, y) / 2
    return loss


def loss_function_gradient(
    G: NDArray[np.float64],
    DG: NDArray[np.float64],
    x: NDArray[np.float64],
) -> NDArray[np.float64]:
    y = x.copy()
    y[-1] = -1
    dx_lin = G[:-1, :] @ y
    dx_nonlin = np.inner(DG @ x, x) / 2
    dx = np.concatenate([dx_lin, [dx_nonlin]])
    return dx


def solve_linear_part(
    G: NDArray[np.float64],
    x: NDArray[np.float64],
) -> NDArray[np.float64]:
    M = G[:-1, :-1]
    u = G[:-1, -1]
    x_sol = np.linalg.solve(M, u)
    x = np.concatenate([x_sol, [x[-1]]])
    return x
