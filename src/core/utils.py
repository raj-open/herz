#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from collections.abc import Iterable
from itertools import chain as itertools_chain
from typing import TypeVar

import numpy as np

from ..thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "characteristic_to_where",
    "flatten",
    "flatten_by_key",
    "gather_by_key",
    "unique",
    "where_to_characteristic",
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar("T")

# ----------------------------------------------------------------
# METHODS - INDICES
# ----------------------------------------------------------------


def where_to_characteristic(indices: list[int] | np.ndarray, N: int) -> list[bool]:
    X = np.asarray([False] * N)
    X[indices] = True
    return X.tolist()


def characteristic_to_where(ch: list[bool] | np.ndarray) -> list[int]:
    obj = np.where(ch)
    return obj[0].tolist()


# ----------------------------------------------------------------
# METHODS - ARRAYS
# ----------------------------------------------------------------


def unique(X: list[T]) -> list[T]:
    X_ = []
    for x in X:
        if x in X_:
            continue
        X_.append(x)
    return X_


def flatten(*X: Iterable[T]) -> list[T]:
    return list(itertools_chain(*X))


def gather_by_key(*X: dict[str, T]) -> dict[str, list[T]]:
    keys = flatten(*[XX.keys() for XX in X])
    keys = unique(keys)
    D = {key: [XX[key] for XX in X if key in X] for key in keys}
    return D


def flatten_by_key(*X: dict[str, list[T]]) -> dict[str, list[T]]:
    G = gather_by_key(*X)
    D = {key: flatten(*values) for key, values in G.items()}
    return D
