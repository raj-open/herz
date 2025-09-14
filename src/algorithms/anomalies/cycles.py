#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from collections.abc import Iterable
from itertools import pairwise

import numpy as np

from ...core.utils import *
from ...thirdparty.maths import *
from .peaks import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "cycles_to_windows",
    "get_cycles",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def cycles_to_windows(
    cycles: Iterable[int],
) -> list[tuple[int, int]]:
    """
    Turns a list indicating cycle indexes into a list
    of pairs of endpoints of the cycles.

    E.g. if the input is `[0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 2]`,
    the output is `[(0, 4), (4, 6), (6, 11)]`.
    """
    c_min = min([*cycles, 0])
    c_max = max([*cycles, 0])
    cycles = [c_min - 1, *cycles, c_max + 1]
    peaks = characteristic_to_where(np.diff(cycles) != 0)
    # DEV-NOTE: equivalent to zip(peaks, peaks[1:])
    windows = list(pairwise(peaks))
    return windows


def get_cycles(
    ext: list[int],
    N: int,
    remove_gaps: bool,
    sig: float = 2.0,
) -> list[int]:
    cycles = -1 * np.ones(shape=(N,), dtype=int)

    # if there is are least 2 extreme points, sift out 'bad' cycles
    if len(ext) > 1:
        # compute order normalised statistics for gaps
        # NOTE: if len(peaks) == 2, then s = [1.]
        s = abs(normalised_order_statistics(np.diff(ext)))

        # remove cycles that are too small or too large
        # DEV-NOTE: equivalent to zip(ext, ext[1:])
        gaps = list(pairwise(ext))
        if remove_gaps:
            gaps = [Id for Id, ss in zip(gaps, s) if ss < sig]

        # enumerate remaining gaps as cycles (all else -> -1)
        for k, (i1, i2) in enumerate(gaps):
            cycles[i1:i2] = k

    # ensure that there is at least one cycle:
    if max(cycles) < 0:
        cycles = np.zeros(shape=(N,), dtype=int)

    return cycles.tolist()
