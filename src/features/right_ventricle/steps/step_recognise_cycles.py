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
from ....algorithms.anomalies import *
from .methods import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_recognise_cycles',
    'step_removed_marked_sections',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP recognise cycles', level=LOG_LEVELS.INFO)
def step_recognise_cycles(
    data: pd.DataFrame,
    quantity: str,
    shift: str,
    remove_gaps: bool = True,
) -> pd.DataFrame:
    N = len(data)

    # get cycles based on peaks (or troughs)
    ext = characteristic_to_where(data[f'{quantity}[{shift}]'])
    cycles = get_cycles(ext=ext, N=N, remove_gaps=remove_gaps)
    data['cycle'] = cycles
    data = data[data['cycle'] >= 0]
    data.reset_index(inplace=True, drop=True)

    # detect 'bad' parts of cycles
    N = len(data)
    # x = data[['pressure', 'volume']].to_numpy(copy=True)
    # marked = mark_pinched_points_on_cycles(x=x, cycles=cycles, sig_t=0.1)
    # data['marked'] = marked
    data['marked'] = [False] * N
    return data


@echo_function(message='STEP remove marked sections', level=LOG_LEVELS.INFO)
def step_removed_marked_sections(
    case: RequestConfig,
    data: pd.DataFrame,
):
    # compute time increment for later
    N = len(data)
    time = data['time'].to_numpy(copy=True)
    _, dt, _ = get_time_aspects(time)

    # remove marked points
    data = data[data['marked'] == False]

    # recompute time axis
    N = len(data)
    T = N * dt
    data = recocompute_time_axis(data, N=N, dt=dt)

    return data
