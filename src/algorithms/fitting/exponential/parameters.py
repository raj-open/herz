#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....models.fitting import *
from ....thirdparty.maths import *
from ....thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_exp_parameters_from_info",
    "fit_exp_parameters_to_info",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_exp_parameters_from_info(
    info: FittedInfoExp,
) -> NDArray[np.float64]:
    """
    Given is the model
    ```
    f(t) = a + b·exp(t/c)
         = a + b·exp(β·t)
            where β = 1/c
    ```
    """
    a = info.vshift
    b = info.vscale
    c = info.hscale
    if c == 0:
        b, beta = 0, 0
    else:
        beta = 1 / c
    return np.asarray([a, b, beta])


def fit_exp_parameters_to_info(
    x: NDArray[np.float64],
) -> FittedInfoExp:
    """
    Given is the model
    ```
    f(t) = a + b·exp(β·t)
         = a + b·exp(t/c)
            where c = 1/β
    ```
    """
    a, b, beta = x
    if beta == 0:
        b, c = 0, 1
    else:
        c = 1 / beta
    return FittedInfoExp(
        hscale=c,
        vscale=b,
        vshift=a,
    )
