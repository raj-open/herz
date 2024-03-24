#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.types import *
from ....thirdparty.maths import *

from ....core.log import *
from ....models.fitting import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'fit_least_sq',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_least_sq(
    mode: EnumSolver,
    scale: float,
    # initialisation
    x_init: NDArray[np.float64],
    # generators
    gen_space: Callable[[], NDArray[np.float64]],
    gen_grad: Callable[[NDArray[np.float64]], tuple[NDArray[np.float64], NDArray[np.float64]]],
    gen_init: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    # solver/loss
    solve_linear_part: Callable[[NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]],
    loss_function: Callable[[NDArray[np.float64], NDArray[np.float64]], float],
    loss_function_grad: Callable[[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]], NDArray[np.float64]],
    restrict_eta: Callable[[float, NDArray[np.float64], NDArray[np.float64]], float],
    # learning parameters
    N_max: int = 1000,
    eta: float = 0.1,
    num_epochs: int = 10,
    eps: float = 0.5e-6,
) -> tuple[NDArray[np.float64], float, float]:
    '''
    Method for `HYBRID_GRADIENT` approach:

    1. nudge params using gradient descent
    2. exactly solve linear-part
    2. L²-difference meets acceptance criteria?
        yes -> stop
        no -> repeat from 1.

    Acceptance criteria:
    Either
    1. (relative) L²-difference < eps
    2. (relative) L²-difference over iterations < eps
    '''
    # determine a size for relativisation of loss:
    best = (x_init, np.inf, np.inf)

    match mode:
        case EnumSolver.BRUTE_FORCE:
            # search for "best" value of ω
            for x in gen_space():
                # compute the exact solution for the linear part of the model
                G, DG = gen_grad(x)
                x = solve_linear_part(G, x)

                # compute loss function and gradient
                loss = loss_function(G, x) / scale
                grad = loss_function_grad(G, DG, x)

                # update best-solution
                dx_norm = np.linalg.norm(grad) / scale
                if loss < best[1] or (loss == best[1] and dx_norm < best[2]):
                    best = (x, loss, dx_norm)

        case EnumSolver.GRADIENT | EnumSolver.HYBRID_GRADIENT:
            dual = mode == EnumSolver.HYBRID_GRADIENT

            # iteratively solve optimisation problem
            for epoch in range(num_epochs):
                log_debug(f'epoch {epoch} started')
                # initialise omega for start of epoch
                x = x_init.copy()
                if epoch > 0:
                    x = gen_init(x)

                # main iteration to move along gradient
                loss = np.inf
                dx_norm = np.inf
                for _ in range(N_max):
                    # compute loss function and gradient
                    G, DG = gen_grad(x)
                    loss = loss_function(G, x) / scale
                    grad = loss_function_grad(G, DG, x)

                    # criteria 1: loss is small -> stop!
                    if loss < eps:
                        break

                    # criteria 2: gradient is sufficiently close to zero -> stop!
                    grad_norm = np.linalg.norm(grad)
                    if grad_norm < eps * scale:
                        break

                    # perform gradient descent
                    dx = -grad
                    eta_eff = restrict_eta(eta, x, dx)
                    dx = eta_eff * dx

                    # criteria 3: stagnant movement (only arises, if near boundary) - cancel learning, retry!
                    dx_norm = np.linalg.norm(dx) / scale
                    if dx_norm < eps:
                        break

                    # otherwise update values
                    x += dx
                    # if hybrid approach used, move linear part to EXACT solution
                    if dual:
                        x = solve_linear_part(G, x)

                if loss < best[1] or (loss == best[1] and dx_norm < best[2]):
                    best = (x, loss, dx_norm)

                log_debug(f'epoch {epoch} finished')

        case EnumSolver():
            raise ValueError(f'No method developed for {mode.value}!')

        case _ as mode:
            raise ValueError(f'No method developed for {mode}!')

    return best
