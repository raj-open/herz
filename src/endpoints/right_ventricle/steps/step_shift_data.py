#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *

from ....setup import config
from ....core.utils import *
from ....models.app import *
from ....models.user import *
from ....queries.fitting import *
from .methods import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_shift_data_extremes',
    'step_shift_data_custom',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def step_shift_data_extremes(
    case: RequestConfig,
    cfg: AppConfig,
    data: pd.DataFrame,
    quantity: str,
    shift: str = 'peak',
) -> pd.DataFrame:
    # compute time increment for later
    N = len(data)
    time = data['time'].to_numpy(copy=True)
    _, dt, _ = get_time_aspects(time)

    # shift data
    ext = characteristic_to_where(data[f'{quantity}[{shift}]'])
    if len(ext) > 0:
        index_max = max(ext)
        indices = list(range(N))
        indices = indices[index_max:] + indices[:index_max]
        data = data.iloc[indices, :]
        data.reset_index(inplace=True, drop=True)
        ext = characteristic_to_where(data[f'{quantity}[{shift}]'])

    # recompute time axis.
    # NOTE: We assume that time has already been homogenised.
    N = len(data)
    data = recocompute_time_axis(data, N=N, dt=dt)
    return data


def step_shift_data_custom(
    case: RequestConfig,
    cfg: AppConfig,
    data: pd.DataFrame,
    points: list[tuple[tuple[int, int], dict[str, int]]],
    quantity: str,
) -> tuple[
    pd.DataFrame,
    list[tuple[tuple[int, int], dict[str, int]]],
]:
    cfg_matching = cfg.settings.matching
    align = get_alignment_point(quantity, cfg=cfg_matching)

    t = data['time'].to_numpy(copy=True)

    # shift times in each cycle
    for k, ((i1, i2), pts) in enumerate(points):
        i0 = pts.get(align, -1)
        if i0 == -1:
            continue
        points[k] = ((i1, i2), {key: i1 + ((i - i0) % (i2 - i1)) for key, i in pts.items()})
        indices = list(range(i1, i2))
        indices = indices[i0:] + indices[:i0]
        data[i1:i2] = data.iloc[indices, :].reset_index(drop=True)

    data['time'] = t

    return data, points
