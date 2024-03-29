#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.data import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...models.fitting import *
from ...models.polynomials import *
from ...models.intervals import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_realignment_intervals',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_realignment_intervals(
    intervals: Iterable[tuple[float, float]],
    t_align: float,
    info: FittedInfoNormalisation,
) -> list[tuple[float, float]]:
    period = info.period
    intervals = [(a - t_align, b - t_align) for a, b in intervals]
    intervals = collapse_intervals_to_cycle(intervals, period=period)
    return intervals
