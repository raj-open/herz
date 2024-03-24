#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'resolve_interval',
    'resolve_intervals',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def resolve_intervals(
    offset: float,
    period: float,
    intervals: Iterable[tuple[float, float]],
) -> Generator[tuple[int, float, float], None, None]:
    for I in intervals:
        yield from resolve_interval(offset=offset, period=period, interval=I)


def resolve_interval(
    offset: float,
    period: float,
    interval: tuple[float, float],
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
