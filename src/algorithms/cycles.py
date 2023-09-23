#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *

from .peaks import *
from ..core.utils import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'cycles_to_windows',
    'get_cycles',
    'mark_pinched_points_on_cycle',
    'mark_pinched_points_on_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def cycles_to_windows(cycles: list[int]) -> list[tuple[int, int]]:
    '''
    Turns a list indicating cycle indexes into a list
    of pairs of endpoints of the cycles.

    E.g. if the input is `[0, 0, 0, 1, 1, 2, 2, 2]`,
    the output is `[(0, 3), (3, 5), (5, 8)]`.
    '''
    c_min = min(cycles + [0])
    c_max = max(cycles + [0])
    cycles = [c_min - 1] + cycles + [c_max + 1]
    peaks = characteristic_to_where(np.diff(cycles) != 0)
    windows = list(zip(peaks, peaks[1:]))
    return windows


def get_cycles(
    peaks: list[int],
    N: int,
    remove_gaps: bool,
    sig: float = 2.0,
) -> list[int]:
    cycles = [-1] * N

    # if there is are least 2 peaks, sift out 'bad' cycles
    if len(peaks) > 1:
        # compute order normalised statistics for gaps
        # NOTE: if len(peaks) == 2, then s = [1.]
        s = np.abs(normalised_order_statistics(np.diff(peaks)))

        # remove cycles that are too small or too large
        gaps = list(zip(peaks, peaks[1:]))
        if remove_gaps:
            gaps = [I for I, ss in zip(gaps, s) if ss < sig]

        # enumerate remaining gaps as cycles (all else -> -1)
        for k, (i1, i2) in enumerate(gaps):
            cycles[i1:i2] = k

    # ensure that there is at least one cycle:
    if max(cycles) < 0:
        cycles = [0] * N

    return cycles


def mark_pinched_points_on_cycles(
    x: np.ndarray,
    cycles: list[int],
    sig_t: float = 0.05,
) -> list[bool]:
    '''
    Cleans 'bad' parts of each cycle.
    '''
    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)
    # mark 'bad' parts of each cycle
    marked = np.concatenate(
        [mark_pinched_points_on_cycle(x=x[i1:i2, :], sig_t=sig_t) for i1, i2 in windows]
    ).tolist()
    return marked


def mark_pinched_points_on_cycle(
    x: np.ndarray,
    sig_t: float = 0.05,
) -> list[bool]:
    '''
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
    '''

    N = x.shape[0]
    m = x.shape[1]
    marked = [False] * N
    d_min = round(1 / sig_t)

    # normalise quantities
    t = np.linspace(start=0, stop=1, num=N, endpoint=False)
    for j in range(m):
        x[:, j] = normalised_order_statistics(x[:, j])

    # compute distance matrices
    dt = np.abs(t[:, np.newaxis] - t)
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
