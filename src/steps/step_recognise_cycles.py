#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..core.utils import *
from ..models.user import *
from ..algorithms.peaks import *
from ..algorithms.cycles import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_recognise_cycles',
    'step_removed_marked_sections',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_recognise_cycles(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
    shift: str,
    remove_gaps: bool = True,
) -> pd.DataFrame:
    # compute time increment for later
    N = len(data)
    t = data['time'].to_numpy(copy=True)
    dt = (t[-1] - t[0]) / (N - 1)

    # 1. detect peaks
    N = len(data)
    values = data[quantity]
    peaks, troughs = get_extremes(values)
    data[f'{quantity}[peak]'] = where_to_characteristic(peaks, N)
    data[f'{quantity}[trough]'] = where_to_characteristic(troughs, N)

    # 2. first shift data to peak-to-peak:
    ext = characteristic_to_where(data[f'{quantity}[{shift}]'])
    if len(ext) > 0:
        index_max = max(ext)
        indices = list(range(N))
        indices = indices[index_max:] + indices[:index_max]
        data = data.iloc[indices, :]
        data.reset_index(inplace=True, drop=True)
        s = N - 1 - index_max
        peaks = [s + i for i in peaks]
        troughs = [s + i for i in troughs]
        data[f'{quantity}[peak]'] = False
        data[f'{quantity}[peak]'][peaks] = True
        data[f'{quantity}[troughs]'] = False
        data[f'{quantity}[troughs]'][troughs] = True
        ext = characteristic_to_where(data[f'{quantity}[{shift}]'])

    # 3. get cycles based on peaks
    N = len(data)
    cycles = get_cycles(ext=ext, N=N, remove_gaps=remove_gaps)
    data['cycle'] = cycles
    data = data[data['cycle'] >= 0]
    data.reset_index(inplace=True, drop=True)

    # 4. mark bad
    # # detect 'bad' parts of cycles
    # N = len(data)
    # x = data[['pressure', 'volume']].to_numpy(copy=True)
    # cycles = data['cycle'].tolist()
    # marked = mark_pinched_points_on_cycles(x=x, cycles=cycles, sig_t=0.1)
    # data['marked'] = marked
    N = len(data)
    data['marked'] = [False] * N

    # 5. recompute time axis.
    # NOTE: we assume that time has already been homogenised.
    N = len(data)
    T_max = N * dt
    data['time[orig]'] = data['time']
    data['time'] = np.linspace(start=0.0, stop=T_max, num=N, endpoint=True)

    return data


def step_removed_marked_sections(
    case: UserCase,
    data: pd.DataFrame,
):
    # compute time increment for later
    N = len(data)
    t = data['time'].to_numpy(copy=True)
    dt = (t[-1] - t[0]) / (N - 1)

    # remove marked points
    data = data[data['marked'] == False]

    # recompute time axis.
    # NOTE: we assume that time has already been homogenised.
    N = len(data)
    T = N * dt
    # data['time[orig]'] = data['time']
    data['time'] = np.linspace(start=0.0, stop=T, num=N, endpoint=False)

    return data
