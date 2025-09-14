#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....models.fitting import *
from ....thirdparty.code import *
from ....thirdparty.maths import *
from ....thirdparty.types import *
from ..leastsq import *
from .geometry import *
from .gradients import *
from .parameters import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_trigonometric_curve",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_trigonometric_curve(
    mode: EnumSolver,
    scale: float,
    # initialisaiton
    fit_init: FittedInfoTrig,
    # generators
    gen_grad: Callable[[NDArray[np.float64]], tuple[NDArray[np.float64], NDArray[np.float64]]],
    # bounds
    omega_min: float,
    omega_max: float,
    # learning parameters
    N_max: int = 1000,
    eta: float = 0.1,
    num_epochs: int = 10,
    eps: float = 0.5e-6,
) -> tuple[FittedInfoTrig, float, float]:
    """
    Runs a least-sq fitting algorithm to fit a trigonometric curve.
    """
    x_init = fit_trig_parameters_from_info(fit_init)

    gen_space = partial(
        generate_space, omega_min=omega_min, omega_max=omega_max, N_max=N_max, x_init=x_init
    )
    gen_init = partial(generate_random_init, omega_min=omega_min, omega_max=omega_max)
    restrict_eta = partial(restrict_learning, omega_min=omega_min, omega_max=omega_max)

    x, loss, dx = fit_least_sq(
        mode=mode,
        scale=scale,
        x_init=x_init,
        gen_space=gen_space,
        gen_grad=gen_grad,
        gen_init=gen_init,
        solve_linear_part=loss_nonlinear_single.solve_linear_part,
        loss_function=loss_nonlinear_single.loss_function,
        loss_function_grad=loss_nonlinear_single.loss_function_gradient,
        restrict_eta=restrict_eta,
        N_max=N_max,
        eta=eta,
        num_epochs=num_epochs,
        eps=eps,
    )

    fit = fit_trig_parameters_to_info(x)

    return fit, loss, dx


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def generate_space(
    omega_min: float,
    omega_max: float,
    x_init: NDArray[np.float64],
    N_max: int,
) -> Generator[NDArray[np.float64], None, None]:
    x_init = x_init.copy()
    for omega in np.linspace(start=omega_min, stop=omega_max, endpoint=True, num=N_max):
        x_init[-1] = omega
        yield x_init


def generate_random_init(
    x: NDArray[np.float64],
    omega_min: float,
    omega_max: float,
) -> NDArray[np.float64]:
    omega = random.uniform(omega_min, omega_max)
    x = np.concatenate([x[:-1], [omega]])
    return x


def restrict_learning(
    eta: float,
    x: NDArray[np.float64],
    dx: NDArray[np.float64],
    omega_min: float,
    omega_max: float,
) -> float:
    if dx[-1] == 0:
        return eta
    # first control how ω changes, preventing explosion
    omega = x[-1]
    dw_max = omega_max - omega
    dw_min = omega_min - omega
    dw = eta * dx[-1]
    dw = max(dw_min, min(dw, dw_max))
    # after applying bound, temporarily recompute learning rate
    eta = abs(dw / dx[-1])
    return eta
