#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from .merge import *
from .resolve import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'collapse_intervals_to_cycle',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def collapse_intervals_to_cycle(
    intervals: Iterable[tuple[float, float]],
    offset: float,
    period: float,
    disjoint: bool = True,
) -> list[tuple[float, float]]:
    '''
    Moves all intervals to the main cycle and resolves these to disjoint intervals.
    '''
    if not disjoint:
        intervals = list(merge_intervals(intervals))
    # make intervals "safely" fit into cycles
    resolution = list(resolve_intervals(offset=offset, period=period, intervals=intervals))
    # move all intervals to first cycle
    intervals = [(a - k * period, b - k * period) for k, a, b in resolution]
    # simplify/merge
    intervals = list(merge_intervals(intervals))
    # sort by endpoints
    intervals = sorted(intervals, key=lambda x: x[0])
    return intervals
