#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...core.utils import *
from ...thirdparty.maths import *
from .cycles import *
from .peaks import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "mark_pinched_points_on_cycle",
    "mark_pinched_points_on_cycles",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def mark_pinched_points_on_cycles(
    x: NDArray[np.float64],
    cycles: list[int],
    sig_t: float = 0.05,
) -> list[bool]:
    """
    Cleans 'bad' parts of each cycle.
    """
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)
    # mark 'bad' parts of each cycle
    marked = np.concatenate(
        [mark_pinched_points_on_cycle(x=x[i1:i2, :], sig_t=sig_t) for i1, i2 in windows]
    ).tolist()
    return marked


def mark_pinched_points_on_cycle(
    x: NDArray[np.float64],
    sig_t: float = 0.05,
) -> list[bool]:
    r"""
    Removes spatial 'pinches' at start/end of parameterised curves.

    The curves are spatial cycles uniformly parameterised by a variable (`t ∈ [0, 1]`).

    @inputs
    - `x` - an `n x d` array. The (implicitly) parameterised set of points in the curve.
    - `sig_t` - a value in `[0, 1]`.
      Two points on a curve at times `t1`, `t2` are considered 'adjacent',
      just in case `0 < |t1 - t2| < sig_t`.

    @returns
    A boolean list which marks which points belong to the 'pinch' (and thereby can be removed).

    What it does:
    Determines two intervals: `[0, t1]` and `[t2, 1]` such that

    1. For each `t[i] ∈ [0, t1] ∪ [t2, 1]` the point `x[i]`
       is sufficiently close to a non-adjacent point on the curve.
    2. For the first times `t[i]` respectively outside these time intervals,
       the point `x[i]` is not sufficiently close to a non-adjacent point.

    NOTE: Pinches that occur mid-cycle are *not* marked!
    """
    N = x.shape[0]
    m = x.shape[1]
    marked = [False] * N
    d_min = round(1 / sig_t)

    # normalise quantities
    t = np.linspace(start=0, stop=1, num=N, endpoint=False)
    for j in range(m):
        x[:, j] = normalised_order_statistics(x[:, j])

    # compute distance matrices
    dt = abs(t[:, np.newaxis] - t)
    dt = np.minimum(dt, 1 - dt)
    dx = np.linalg.norm(x[:, np.newaxis] - x, axis=2) / math.sqrt(m)

    # NOTE: artificially increase curve-distance values of adjacent-points
    # to avoid these being candidates for detecting pinches.
    C = np.max(dx) + 1.0
    dx[(0 < dt) & (dt < sig_t)] = 2 * C

    # NOTE: Search in window from start for points that are
    # 'close' to non-adjacent points on curve.
    for i in range(N):
        peaks = get_peaks_simple(C - dx[i, :], add_end=False, distance=d_min, prominence=0.5)
        if peaks == [i] or len(peaks) == 0:
            break
        marked[i] = True

    # NOTE: Search in window from end for points that are
    # 'close' to non-adjacent points on curve.
    for i in range(N)[::-1]:
        peaks = get_peaks_simple(C - dx[i, :], add_end=False, distance=d_min, prominence=0.5)
        if peaks == [i] or len(peaks) == 0:
            break
        marked[i] = True

    return marked
