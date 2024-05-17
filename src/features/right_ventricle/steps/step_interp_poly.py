#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.code import *
from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.types import *

from ....core.log import *
from ....core.constants import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....algorithms.anomalies import *
from ....algorithms.fitting.trigonometric import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_interp_poly',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP fit interpolated poly-model to data', level=LOG_LEVELS.INFO)
def step_interp_poly(
    data: pd.DataFrame,
    special: dict[str, SpecialPointsConfig],
    symb: str,
    cfg_fit: InterpConfigTrig,
) -> tuple[
    FittedInfoTrig,
    list[tuple[float, float]],
    list[tuple[float, float]],
]:
    '''
    Fits an interpolated polynomial curve to normalised model.
    '''
    # TODO
    return


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def message_result(
    fit: FittedInfoTrig,
    loss: float,
    dx: float,
):
    return dedent(
        f'''
        Parameters of trigonometric model:
        (  Shift/Linear + Oscillation  )
        ----
        period:    {fit.hscale}
        amplitude: {fit.vscale}
        iso-max:   ({fit.hshift}, {fit.vshift + fit.vscale})
        ----
        Relativised loss of the approximation: {loss:.4g}
        Final movement of parameters during computation: {dx:.4e}
        '''
    )


def restrict_data_to_intervals(
    data: pd.DataFrame,
    intervals: Iterable[tuple[float, float]],
    offset: float,
    period: float,
) -> NDArray[np.float64]:
    '''
    Restricts time and values of data to intervals.
    '''
    # filter data
    intervals_ = [(offset + (a - offset) % period, offset + (b - offset) % period) for a, b in intervals]
    data = np.asarray(
        [
            data['time'],
            data['dt'],
            data['value'],
        ]
    ).T
    datas = [data[(a_ <= data[:, 0]) & (data[:, 0] < b_), :] for a_, b_ in intervals_]
    # rewrite time-values
    times = [data[:, 0] + (a - a_) for (a, b), (a_, b_), data in zip(intervals, intervals_, datas)]
    delta = [data[:, 1] for data in datas]
    values = [data[:, 2] for data in datas]
    # store in data structure
    data = np.row_stack([np.column_stack([t, dt, x]) for t, dt, x in zip(times, delta, values)])
    return data
