#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import math
from collections.abc import Iterable

import numpy as np
from numpy.typing import NDArray
from scipy import signal as sps

from ...thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "get_extremes",
    "get_peaks_simple",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_extremes(
    values: NDArray[np.float64],
    sig_width: float = 1 / math.sqrt(2),
) -> tuple[list[int], list[int]]:
    N_values = len(values)
    # first make data as symmetric as possible
    values = normalised_order_statistics(values)
    # preliminary computation of peaks
    peaks = get_peaks_simple(abs(values))
    # estimate cycle length
    peaks.append(N_values)
    N = estimate_cycle_duration(peaks) or N_values
    width = round(sig_width * N) or 1.0
    # re-compute peaks
    peaks = get_peaks_simple(values, distance=width, prominence=1)
    troughs = get_peaks_simple(-values, distance=width, prominence=1)
    return peaks, troughs


def get_peaks_simple(values: NDArray[np.float64], **kwargs) -> list[int]:
    N = len(values)

    result = sps.find_peaks(
        values,
        **kwargs,
        # height=None,
        # threshold=None,
        # distance=None,
        # prominence=None,
        # width=None,
        # wlen=None,
        # rel_height=0.5,
        # plateau_size=None,
    )
    peaks = result[0].tolist()

    # force list to be non-empty, if possible.
    if len(peaks) == 0 and len(values) > 0:
        index_max = np.asarray(values).argmax()
        peaks = [index_max]

    return peaks


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def estimate_cycle_duration(peaks: Iterable) -> int:
    N = 0
    if len(peaks) > 1:
        # compute differences between elements
        delta = np.diff(peaks)
        # remove outliers
        delta = remove_outliers(delta)
        # compute minimal difference (excl. outliers)
        N = round(min(delta))
    return N
