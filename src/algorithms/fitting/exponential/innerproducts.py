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
    'compute_inner_products_from_model',
    'compute_inner_products_from_data',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def compute_inner_products_from_model(
    models: list[Poly[float]],
    intervals: list[tuple[float, float]],
    beta: float,
) -> dict[set, float]:
    raise Exception('Not yet implemented!')


def compute_inner_products_from_data(
    data: NDArray[np.float64],
    beta: float,
) -> dict[set, float]:
    raise Exception('Not yet implemented!')
