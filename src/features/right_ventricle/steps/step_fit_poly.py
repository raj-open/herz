#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....core.log import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....algorithms.anomalies import *
from ....algorithms.fitting.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_fit_poly',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP fit polynomial-model to data', level=LOG_LEVELS.INFO)
def step_fit_poly(
    data: pd.DataFrame,
    quantity: str,
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    mode: EnumFittingMode,
    n_der: int,
) -> tuple[pd.DataFrame, list[tuple[tuple[int, int], FittedInfoPoly]]]:
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
    fits = fit_poly_cycles(t=t, x=x, windows=windows, conds=conds)

    # compute n'th derivatives
    data = compute_nth_derivatives_for_cycles(data, fits, quantity=quantity, n_der=n_der, mode=mode)

    return data, fits


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def compute_nth_derivatives_for_cycles(
    data: pd.DataFrame,
    fits: list[tuple[tuple[int, int], FittedInfoPoly]],
    quantity: str,
    n_der: int,
    mode: EnumFittingMode,
) -> pd.DataFrame:
    '''
    Computes the n'th derivatives of the fitted curve for each cycle.
    '''
    N = len(data)
    t = data['time'].to_numpy(copy=True)

    match mode:
        case EnumFittingMode.AVERAGE:
            _, fit = fits[-1]
            infos = [((i1, i2), fit.coefficients[:]) for (i1, i2), _ in fits[:-1]]
        case _:
            infos = [((i1, i2), fit.coefficients[:]) for (i1, i2), fit in fits[:-1]]

    data[f'{quantity}[fit]'] = np.zeros(t.shape)
    for n in range(1, n_der + 1):
        data[f'd[{n},t]{quantity}[fit]'] = np.zeros(t.shape)

    # loop over all time-subintervals and compute the n'th derivatives
    for (i1, i2), coeff in infos:
        p = p = Poly[float](coeff=coeff)
        tt = t[i1:i2]

        col = f'{quantity}[fit]'
        data[col][i1:i2] = p.values(tt)
        for n in range(1, n_der + 1):
            p = p.derivative()
            col = f'd[{n},t]{quantity}[fit]'
            data[col][i1:i2] = p.values(tt)

    return data
