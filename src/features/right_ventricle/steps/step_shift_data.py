#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *

from ....core.log import *
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


@echo_function(message='STEP shift data to extremes ({shift})', level=LOG_LEVELS.INFO)
def step_shift_data_extremes(
    data: pd.DataFrame,
    quantity: str,
    shift: str = 'peak',
) -> pd.DataFrame:
    # compute time increment for later
    N = len(data)
    time = data['time'].to_numpy(copy=True)

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
    _, _, dt = get_time_aspects(time)
    data = recocompute_time_axis(data, dt=dt)
    return data


@echo_function(message='STEP shift data to matching points', level=LOG_LEVELS.INFO)
def step_shift_data_custom(
    data: pd.DataFrame,
    points: list[tuple[tuple[int, int], dict[str, int]]],
) -> pd.DataFrame:

    # create copies so that original data not affected
    data = data.copy(True)
    t_orig = data['time[orig]'].to_numpy(copy=True)
    t = data['time'].to_numpy(copy=True)

    # shift times in each cycle
    for (i1, i2), index in points:
        i0 = index.get('align', -1)
        if i0 == -1:
            continue
        indices = list(range(i1, i2))
        indices = indices[i0:] + indices[:i0]
        data[i1:i2] = data.iloc[indices, :].reset_index(drop=True)

    data['time[orig]'] = t_orig
    data['time'] = t

    return data
