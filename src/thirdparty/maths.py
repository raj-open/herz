#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import lmfit
import math
import numpy as np
import random
import scipy as sp
from scipy import linalg as spla
from scipy import optimize as spo
from scipy import signal as sps
from findpeaks import findpeaks

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def nCr(n: int, r: int) -> int:
    '''
    Computes `n!/(r!(n-r)!)`
    '''
    return math.comb(n, r)


def nPr(n: int, r: int) -> int:
    '''
    Computes `n!/(n-r)!`
    '''
    if r == 0:
        return 1
    if r == 1:
        return n
    return math.factorial(r) * math.comb(n, r)


def normalised_order_statistics(X: np.ndarray) -> np.ndarray:
    '''
    Computes

    ```
    s = (X - m) / scale
    ```

    where

    - `m` = median of `X`
    - `scale` = median of `|X - m|` (or `1` if this is `0`)

    This measures how close (relatively) a random variable is to its median.
    Working with medians for the scale prevent warping effects from outliers.

    NOTE:
    - If `X` contains `1` element, then `s = [0]`.
    - If `X` contains `2` elements,
      then `s = [1, 1]` if the values are different
      or else `s = [0, 0]`.
    '''
    med = np.median(X)
    delta = X - med
    scale = np.median(np.abs(delta)) or 1.0
    s = delta / scale
    return s


def indices_non_outliers(X: np.ndarray, sig: float = 2.0) -> list[int]:
    '''
    Computes indices of all elements in an array,
    bar those which are significantly far away from the median.

    NOTE: Choose `sig > 1`.

    NOTE:
    - If `X` contains `<= 2` elements, then nothing is removed.
    - If `X` is non-empty,
      then the result contains at least the elements
      closest to the median.
    '''
    s = np.abs(normalised_order_statistics(X))
    obj = np.where(s < sig)
    return obj[0].tolist()


def remove_outliers(X: np.ndarray, sig: float = 2.0) -> np.ndarray:
    '''
    Removes elements from an array which are significantly far away from the median.

    NOTE: Choose `sig > 1`.

    NOTE:
    - If `X` contains `<= 2` elements, then nothing is removed.
    - If `X` is non-empty,
      then the result contains at least the elements
      closest to the median.
    '''
    indices = indices_non_outliers(X, sig=sig)
    X = X[indices]
    return X


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'findpeaks',
    'lmfit',
    'math',
    'nCr',
    'nPr',
    'normalised_order_statistics',
    'np',
    'random',
    'indices_non_outliers',
    'remove_outliers',
    'sp',
    'spla',
    'spo',
    'sps',
]
