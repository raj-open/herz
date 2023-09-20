#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from .peaks import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'clean_cycles',
    'get_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def clean_cycles(
    data: pd.DataFrame,
    parameter: str,
    quantities: list[str],
    peaks: list[int],
    sig_t: float = 0.05,
):
    N = len(data)
    theta = data[parameter].to_numpy(copy=True)
    values = data[quantities].to_numpy(copy=True)

    if len(peaks) <= 1:
        gaps = [(0, N)]
    else:
        gaps = [(i1, i2) for i1, i2 in zip(peaks, peaks[1:])]

    marked = np.asarray([False] * N)

    for i1, i2 in gaps:
        # consider cycle
        n = i2 - i1
        t = theta[i1:i2]
        x = values[i1:i2, :]

        # normalise quantities
        m = x.shape[1]
        t -= min(t)
        if len(t) > 1:
            t = t / (max(t) or 1.0)
        for j in range(m):
            x[:, j] = normalised_order_statistics(x[:, j])

        # compute distance matrices
        dt = np.abs(t[:, np.newaxis] - t)
        dt = np.minimum(dt, 1 - dt)
        dx = np.linalg.norm(x[:, np.newaxis] - x, axis=2) / math.sqrt(m)
        C = np.max(dx) + 1.0
        dx[(0 < dt) & (dt < sig_t)] = 2 * C

        for i in range(n):
            peaks = get_peaks_simple(
                C - dx[i, :], add_end=False, distance=round(1 / sig_t), prominence=0.5
            )
            if i in peaks:
                peaks.remove(i)
            if len(peaks) == 0:
                break
            marked[i1 + i] = True

        for i in range(n)[::-1]:
            peaks = get_peaks_simple(
                C - dx[i, :], add_end=False, distance=round(1 / sig_t), prominence=0.5
            )
            if i in peaks:
                peaks.remove(i)
            if len(peaks) == 0:
                break
            marked[i1 + i] = True

    data['marked'] = marked

    return data


def get_cycles(
    peaks: list[int],
    N: int,
    remove_gaps: bool,
    sig: float = 2.0,
) -> np.ndarray:
    cycles = -1 * np.ones(shape=(N,), dtype=int)

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
        cycles = np.zeros(shape=(N,), dtype=int)

    return cycles
