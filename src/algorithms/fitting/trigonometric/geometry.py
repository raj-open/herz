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
    "compute_inner_products_from_model",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def compute_inner_products_from_model(
    models: list[Poly[float]],
    intervals: list[tuple[float, float]],
    omega: float,
) -> dict[set, float]:
    # create models
    ONE = Poly(coeff=[1])
    t = Poly(coeff=[0, 1])
    t2 = Poly(coeff=[0, 0, 1])
    tp = [Poly[float].cast(t * q) for q in models]
    C1 = Cos(omega=omega)
    S1 = Sin(omega=omega)
    C2 = Cos(omega=2 * omega)
    S2 = Sin(omega=2 * omega)

    # compute simple integrals
    I_one = ONE.integral().evaluate(*intervals)
    I_t = t.integral().evaluate(*intervals)
    I_t2 = t2.integral().evaluate(*intervals)
    I_cos = C1.integral().evaluate(*intervals)
    I_sin = S1.integral().evaluate(*intervals)
    I_cos2 = C2.integral().evaluate(*intervals)
    I_sin2 = S2.integral().evaluate(*intervals)
    I_p = sum([q.integral().evaluate(I) for q, I in zip(models, intervals)])  # fmt: skip
    I_p2 = sum([(q * q).integral().evaluate(I) for q, I in zip(models, intervals)])  # fmt: skip
    I_tp = sum([tq.integral().evaluate(I) for tq, I in zip(tp, intervals)])  # fmt: skip
    I_t_cos = (C1 * t).integral().evaluate(*intervals)
    I_t_sin = (S1 * t).integral().evaluate(*intervals)
    I_t2_cos = (C1 * t2).integral().evaluate(*intervals)
    I_t2_sin = (S1 * t2).integral().evaluate(*intervals)
    I_p_cos = sum([(C1 * q).integral().evaluate(I) for q, I in zip(models, intervals)])  # fmt: skip
    I_p_sin = sum([(S1 * q).integral().evaluate(I) for q, I in zip(models, intervals)])  # fmt: skip
    I_tp_cos = sum([(C1 * tq).integral().evaluate(I) for tq, I in zip(tp, intervals)])  # fmt: skip
    I_tp_sin = sum([(S1 * tq).integral().evaluate(I) for tq, I in zip(tp, intervals)])  # fmt: skip
    I_t_cos2 = (C2 * t).integral().evaluate(*intervals)
    I_t_sin2 = (S2 * t).integral().evaluate(*intervals)

    # --------------------------------
    # compute product trig integrals
    # NOTE:
    # cos(ωt)cos(ωt) = ½(1 + cos(2ωt))
    # sin(ωt)sin(ωt) = ½(1 - cos(2ωt))
    # sin(ωt)cos(ωt) = ½·sin(2ωt)
    # --------------------------------
    I_cos_cos = (I_one + I_cos2) / 2
    I_sin_sin = (I_one - I_cos2) / 2
    I_cos_sin = I_sin2 / 2
    I_t_cos_sin = I_t_sin2 / 2
    I_t_cos_cos = (I_t + I_t_cos2) / 2
    I_t_sin_sin = (I_t - I_t_cos2) / 2

    # place innerproducts in dict
    return {
        "1": I_one,
        "t": I_t,
        "cos": I_cos,
        "sin": I_sin,
        "f": I_p,
        "t^2": I_t2,
        "cos^2": I_cos_cos,
        "sin^2": I_sin_sin,
        "f^2": I_p2,
        "cos*sin": I_cos_sin,
        "t*cos": I_t_cos,
        "t*sin": I_t_sin,
        "t*f": I_tp,
        "f*cos": I_p_cos,
        "f*sin": I_p_sin,
        "t*f*cos": I_tp_cos,
        "t*f*sin": I_tp_sin,
        "t*cos^2": I_t_cos_cos,
        "t*sin^2": I_t_sin_sin,
        "t*cos*sin": I_t_cos_sin,
        "t^2*cos": I_t2_cos,
        "t^2*sin": I_t2_sin,
    }


def compute_inner_products_from_data(
    data: NDArray[np.float64],
    omega: float,
) -> dict[set, float]:
    t, dt, x = data[:, 0], data[:, 1], data[:, 2]
    t2 = t**2
    tx = t * x
    # create models
    C1 = np.cos(omega * t)
    S1 = np.sin(omega * t)
    C2 = np.cos(2 * omega * t)
    S2 = np.sin(2 * omega * t)

    # compute simple integrals
    I_one = np.sum(dt)
    I_t = np.sum(t * dt)
    I_t2 = np.sum(t2 * dt)
    I_x = np.sum(x * dt)
    I_x2 = np.sum((x**2) * dt)
    I_tx = np.sum(tx * dt)
    I_cos = np.sum(C1 * dt)
    I_sin = np.sum(S1 * dt)
    I_cos2 = np.sum(C2 * dt)
    I_sin2 = np.sum(S2 * dt)
    I_t_cos = np.sum(t * C1 * dt)
    I_t_sin = np.sum(t * S1 * dt)
    I_x_cos = np.sum(x * C1 * dt)
    I_x_sin = np.sum(x * S1 * dt)
    I_tx_cos = np.sum(tx * C1 * dt)
    I_tx_sin = np.sum(tx * S1 * dt)
    I_t_cos2 = np.sum(t * C2 * dt)
    I_t_sin2 = np.sum(t * C2 * dt)
    I_t2_cos = np.sum(t2 * C1 * dt)
    I_t2_sin = np.sum(t2 * S1 * dt)
    # --------------------------------
    # compute product trig integrals
    # NOTE:
    # cos(ωt)cos(ωt) = ½(1 + cos(2ωt))
    # sin(ωt)sin(ωt) = ½(1 - cos(2ωt))
    # sin(ωt)cos(ωt) = ½·sin(2ωt)
    # --------------------------------
    I_cos_cos = (I_one + I_cos2) / 2
    I_sin_sin = (I_one - I_cos2) / 2
    I_cos_sin = I_sin2 / 2
    I_t_cos_sin = I_t_sin2 / 2
    I_t_cos_cos = (I_t + I_t_cos2) / 2
    I_t_sin_sin = (I_t - I_t_cos2) / 2

    # place innerproducts in dict
    return {
        "1": I_one,
        "t": I_t,
        "cos": I_cos,
        "sin": I_sin,
        "f": I_x,
        "t^2": I_t2,
        "cos^2": I_cos_cos,
        "sin^2": I_sin_sin,
        "f^2": I_x2,
        "cos*sin": I_cos_sin,
        "t*cos": I_t_cos,
        "t*sin": I_t_sin,
        "t*f": I_tx,
        "f*cos": I_x_cos,
        "f*sin": I_x_sin,
        "t*f*cos": I_tx_cos,
        "t*f*sin": I_tx_sin,
        "t*cos^2": I_t_cos_cos,
        "t*sin^2": I_t_sin_sin,
        "t*cos*sin": I_t_cos_sin,
        "t^2*cos": I_t2_cos,
        "t^2*sin": I_t2_sin,
    }
