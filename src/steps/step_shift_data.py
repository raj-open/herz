#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..core.log import *
from ..core.utils import *
from ..models.user import *
from .methods import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_shift_data_extremes',
    'step_shift_data_custom',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_shift_data_extremes(
    case: UserCase,
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
    case: UserCase,
    data: pd.DataFrame,
    points: dict[str, list[int]],
    quantity: str,
) -> pd.DataFrame:
    log_warn('Not yet implemented')
    return data
