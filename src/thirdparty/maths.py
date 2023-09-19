#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import math
import numpy as np
import random
import scipy as sp
from scipy import signal as sps
from findpeaks import findpeaks

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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
    s = np.abs(normalised_order_statistics(X))
    X = X[s < sig]
    return X


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'findpeaks',
    'math',
    'np',
    'random',
    'normalised_order_statistics',
    'remove_outliers',
    'sp',
    'sps',
]