#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Loss functions and their gradients
for models with non-linear parts governed by a single-parameter.
Assumes that in the vector of parameters to be fitted,
the parameter for the non-linearity occurs last.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.maths import *
from ....thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'loss_function',
    'loss_function_gradient',
    'solve_linear_part',
]

# ----------------------------------------------------------------
# METHODS
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
    # NOTE: G is positive, but may have 0 as eigenvalue, so solve using least-sq
    # x_sol = np.linalg.solve(M, u)
    x_sol, _, _, _ = np.linalg.lstsq(M, u)
    x = np.concatenate([x_sol, [x[-1]]])
    return x
