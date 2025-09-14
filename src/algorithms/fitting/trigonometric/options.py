#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....models.polynomials import *
from ....thirdparty.maths import *
from ....thirdparty.types import *
from .geometry import *
from .gradients import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_options_gradients_data",
    "fit_options_gradients_poly_model",
    "fit_options_scale_data",
    "fit_options_scale_poly_model",
]

# ----------------------------------------------------------------
# METHODS - DATA
# ----------------------------------------------------------------


def fit_options_scale_data(
    data: NDArray[np.float64],
) -> float:
    """
    Determines the L²-norm of the data curves.
    Useful for scaling the loss function and errors.
    """
    t, dt, x = data[:, 0], data[:, 1], data[:, -1]
    T = max(t) - min(t) + np.mean(dt)
    norm_x = math.sqrt(np.sum((x**2) * dt) / T)
    return norm_x


def fit_options_gradients_data(
    data: NDArray[np.float64],
    drift: bool,
) -> Callable[[float], tuple[NDArray[np.float64], NDArray[np.float64]]]:
    def method(x: NDArray[np.float64]):
        omega = x[-1]
        ip = compute_inner_products_from_data(data=data, omega=omega)
        G = inner_product_matrix(ip, drift)
        DG = inner_product_matrix_derivative(ip, drift)
        return G, DG

    return method


# ----------------------------------------------------------------
# METHODS - POLY
# ----------------------------------------------------------------


def fit_options_scale_poly_model(
    models: list[Poly[float]],
    intervals: list[tuple[float, float]],
) -> float:
    """
    Determines the L²-norm of the polynomial model.
    Useful for scaling the loss function and errors.
    """
    norm_p = math.sqrt(
        sum(
            (q * q).integral().evaluate(interval)
            for q, interval in zip(models, intervals)
        )
    )  # fmt: skip
    return norm_p


def fit_options_gradients_poly_model(
    models: list[Poly[float]],
    intervals: list[tuple[float, float]],
    drift: bool,
) -> Callable[[float], tuple[NDArray[np.float64], NDArray[np.float64]]]:
    """
    Provides a callback function that computes the innerproducts
    for a given
    """

    def method(x: NDArray[np.float64]):
        omega = x[-1]
        ip = compute_inner_products_from_model(models=models, intervals=intervals, omega=omega)
        G = inner_product_matrix(ip, drift)
        DG = inner_product_matrix_derivative(ip, drift)
        return G, DG

    return method
