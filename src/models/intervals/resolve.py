#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import math
from collections.abc import Iterable
from typing import Generator

from ...thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "resolve_interval",
    "resolve_intervals",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def resolve_intervals(
    intervals: Iterable[tuple[float, float]],
    period: float,
    offset: float = 0.0,
) -> Generator[tuple[int, float, float], None, None]:
    for interval in intervals:
        yield from resolve_interval(interval, offset=offset, period=period)


def resolve_interval(
    interval: tuple[float, float],
    period: float,
    offset: float = 0.0,
) -> Generator[tuple[int, float, float], None, None]:
    a, b = interval
    k = math.floor((a - offset) / period)
    t0 = offset + k * period
    while t0 < b:
        t1 = max(a, t0)
        t2 = min(t0 + period, b)
        if t1 < t2:
            yield k, t1, t2
        k += 1
        t0 = offset + k * period
    return
