#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *

from ....core.log import *
from ....models.fitting import *
from ....algorithms.anomalies import *
from ....algorithms.fitting.normalisation import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_normalise',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP normalise time-{quantity} cycles', level=LOG_LEVELS.INFO)
def step_normalise(
    data: pd.DataFrame,
    quantity: str,
) -> tuple[
    pd.DataFrame,
    list[tuple[FittedInfoNormalisation, tuple[int, int]]],
]:
    '''
    Fits polynomial to cycles in time-series, forcing certain conditions
    on the `n`th-derivatives at certain time points,
    and minimising wrt. the L²-norm.

    NOTE: Initial fitting runs from peak to peak.
    '''
    # fit polynomial
    t = data['time'].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)
    cycles = data['cycle'].tolist()
    windows = cycles_to_windows(cycles)
    t, dt, x, fitinfos = fit_normalisation(t=t, x=x, windows=windows)

    data['time'] = t
    data['dt'] = dt
    data[quantity] = x

    return data, fitinfos
