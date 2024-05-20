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
    'step_refit_poly',
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
    intervals: Iterable[tuple[float, float]] = [(0, 1)],
) -> tuple[pd.DataFrame, list[tuple[Poly[float], tuple[int, int]]]]:
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
    fits = fit_poly_cycles(t=t, x=x, windows=windows, conds=conds, intervals=intervals)

    # compute n'th derivatives
    data = compute_nth_derivatives_for_cycles(data, fits, quantity=quantity, n_der=n_der, mode=mode)

    return data, fits


@echo_function(message='STEP re-fit polynomial-model to data via interpolation', level=LOG_LEVELS.INFO)
def step_refit_poly(
    data: pd.DataFrame,
    quantity: str,
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    mode: EnumFittingMode,
    n_der: int,
    period: float,
    cfg: InterpConfigPoly,
    special: dict[str, SpecialPointsConfig],
) -> tuple[pd.DataFrame, list[tuple[Poly[float], tuple[int, int]]]]:
    '''
    Re-fits polynomial to data series interpolating between certain special points.
    '''
    # determine the intervals (normalised)
    key1, key2 = cfg.interval.root
    pt1, pt2 = special[key1], special[key2]
    intervals = [(pt1.time / period, pt2.time / period)]

    # force conditions (use normalised time values)
    conds_ = []
    for pt in [pt1, pt2]:
        conds_.append(PolyDerCondition(derivative=pt.spec.derivative, time=pt.time / period))
    conds = conds + conds_

    # run the fit method
    return step_fit_poly(data=data, quantity=quantity, conds=conds, mode=mode, n_der=n_der, intervals=intervals)  # fmt: skip


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def compute_nth_derivatives_for_cycles(
    data: pd.DataFrame,
    fitsinfos: list[tuple[Poly[float], tuple[int, int]]],
    quantity: str,
    n_der: int,
    mode: EnumFittingMode,
) -> pd.DataFrame:
    '''
    Computes the n'th derivatives of the fitted curve for each cycle.
    '''
    t = data['time'].to_numpy(copy=True)

    match mode:
        case EnumFittingMode.AVERAGE:
            p, _ = fitsinfos[-1]
            fitsinfos = [(p, win) for _, win in fitsinfos[:-1]]
        case _:
            pass

    data[f'{quantity}[fit]'] = np.zeros(t.shape)
    for n in range(1, n_der + 1):
        data[f'd[{n},t]{quantity}[fit]'] = np.zeros(t.shape)

    # loop over all time-subintervals and compute the n'th derivatives
    for p, (i1, i2) in fitsinfos:
        tt = t[i1:i2]
        col = f'{quantity}[fit]'
        data[col][i1:i2] = p.values(tt)
        for n in range(1, n_der + 1):
            p = p.derivative()
            col = f'd[{n},t]{quantity}[fit]'
            data[col][i1:i2] = p.values(tt)

    return data
