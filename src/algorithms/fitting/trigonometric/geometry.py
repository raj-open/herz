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
    'resteer_towards_solution_linear_part',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def inner_product_matrix(
    ip: dict[set, float],
    drift: bool,
) -> NDArray[np.float64]:
    '''
    Computes inner product matrix, useful for computing

    1. loss function.
    2. gradient of linear part of model.

    NOTE: mathematically, `G` is a positive matrix!
    (Verified numerically.)
    '''
    G = np.asarray(
        [
            [
                ip['1'],
                ip['t'],
                ip['cos'],
                ip['sin'],
                ip['f'],
            ],
            [
                ip['t'],
                ip['t^2'],
                ip['t*cos'],
                ip['t*sin'],
                ip['t*f'],
            ],
            [
                ip['cos'],
                ip['t*cos'],
                ip['cos^2'],
                ip['cos*sin'],
                ip['f*cos'],
            ],
            [
                ip['sin'],
                ip['t*sin'],
                ip['cos*sin'],
                ip['sin^2'],
                ip['f*sin'],
            ],
            [
                ip['f'],
                ip['t*f'],
                ip['f*cos'],
                ip['f*sin'],
                ip['f^2'],
            ],
        ]
    )

    # deactivate contribute by drift term
    if not drift:
        G[1, :] = 0
        G[:, 1] = 0
        G[1, 1] = 1

    return G


def inner_product_matrix_derivative(
    ip: dict[set, float],
    drift: bool,
) -> NDArray[np.float64]:
    '''
    Computes derivative of the inner product matrix wrt. ω.
    '''
    DG = np.asarray(
        [
            [
                0,
                0,
                -ip['t*sin'],
                ip['t*cos'],
                0,
            ],
            [
                0,
                0,
                -ip['t^2*sin'],
                ip['t^2*cos'],
                0,
            ],
            [
                -ip['t*sin'],
                -ip['t^2*sin'],
                -2 * ip['t*cos*sin'],
                ip['t*cos^2'] - ip['t*sin^2'],
                -ip['t*f*sin'],
            ],
            [
                ip['t*cos'],
                ip['t^2*sin'],
                ip['t*cos^2'] - ip['t*sin^2'],
                2 * ip['t*cos*sin'],
                ip['t*f*cos'],
            ],
            [
                0,
                0,
                -ip['t*f*sin'],
                ip['t*f*cos'],
                0,
            ],
        ]
    )

    # deactivate contribute by drift term
    if not drift:
        DG[1, :] = 0
        DG[:, 1] = 0

    return DG


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
    y[-1] = 1
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


def resteer_towards_solution_linear_part(
    x: NDArray[np.float64],
    sol: NDArray[np.float64],
    dx: NDArray[np.float64],
):
    '''
    Adjusts the gradient in such a way, that

    1. `-grad` for the linear parameters
        points in the direction of the exact solution.

    2. `‖grad‖` is conserved.
    '''
    dw = dx[-1]
    delta = sol - x[:-1]
    C_sol = np.linalg.norm(delta)
    C = np.linalg.norm(dx[:-1])
    r = C / (C_sol or 1)
    dx = np.concatenate([-r * delta, [dw]])
    return dx
