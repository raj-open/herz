#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np
from numpy.typing import NDArray

from ....models.fitting import *
from ....models.polynomials import *
from ....thirdparty.maths import *
from ...interpolations import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "fit_normalisation",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def fit_normalisation(
    t: NDArray[np.float64],
    x: NDArray[np.float64],
    windows: list[tuple[int, int]],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    list[tuple[FittedInfoNormalisation, tuple[int, int]]],
]:
    """
    Fits polynomial to cycles of a time-series:
    - minimises wrt. the L²-norm
    - forces certain conditions on n'th-derivatives at certain time points
    """
    # fit each cycle
    fitinfos = []
    dt = np.zeros(t.shape)
    for i1, i2 in windows:
        # scale time
        tt, _, T, _ = normalise_to_unit_interval(t[i1:i2])

        # scale values
        c, m, s, xx = normalise_interpolated_cycle(tt, x[i1:i2], T=1, periodic=True)
        x[i1:i2] = xx
        t[i1:i2] = tt
        if len(tt) > 1:
            dt_ = tt[1:] - tt[:-1]
            dt__ = (dt_[1:] + dt_[:-1]) / 2
            dt_ = np.concatenate([[dt_[0]], dt__, [dt_[-1]]])
        else:
            dt_ = np.ones(tt.shape)
        dt[i1:i2] = dt_

        # compute fitted curve
        info = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
        fitinfos.append((info, (i1, i2)))

    info = combine_fit([info for info, _ in fitinfos])
    fitinfos.append((info, (-1, -1)))

    return t, dt, x, fitinfos


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def combine_fit(infos: list[FittedInfoNormalisation]) -> FittedInfoNormalisation:
    """
    Fits a single polynomial to all (normalised) cycles simultaenously.
    """
    T = np.median(np.asarray([info.period for info in infos]), axis=0).tolist()  # fmt: skip
    c = np.median(np.asarray([info.intercept for info in infos]), axis=0).tolist()  # fmt: skip
    m = np.median(np.asarray([info.gradient for info in infos]), axis=0).tolist()  # fmt: skip
    s = np.median(np.asarray([info.scale for info in infos]), axis=0).tolist()  # fmt: skip
    info = FittedInfoNormalisation(period=T, intercept=c, gradient=m, scale=s)
    return info
