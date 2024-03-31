#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.maths import *
from ....thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'inner_product_matrix',
    'inner_product_matrix_derivative',
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
        val = G[1, 1]
        G[1, :] = 0
        G[:, 1] = 0
        G[1, 1] = val

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
