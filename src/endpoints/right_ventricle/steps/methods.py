#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....core.utils import *
from ....models.user import *
from ....algorithms.peaks import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_time_aspects',
    'recocompute_time_axis',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_time_aspects(
    t: Iterable[float],
    ordered: bool = True,
    endpoint: bool = False,
) -> tuple[int, float, float]:
    '''
    Computes aspects

    - `N` - number of points
    - `dt` - time increment (assuming homogeneity)
    - `T_max` - total duration

    of an ordered series of time points
    '''
    if len(t) == 0:
        return 0, 0.0, 0.0
    N = len(t)
    T_max = t[-1] - t[0] if ordered else max(t) - min(t)
    if endpoint:
        # adjust N
        N = N - 1
    else:
        # initial guess of dt
        dt = np.median(np.diff(t))
        # correct T_max
        T_max += dt
    # compute dt
    dt = T_max / (N or 1.0)
    return N, dt, T_max


def recocompute_time_axis(
    data: pd.DataFrame,
    N: int,
    dt: float,
) -> pd.DataFrame:
    T_max = N * dt
    data['time[orig]'] = data['time']
    data['time'] = np.linspace(start=0.0, stop=T_max, num=N, endpoint=False)
    return data
