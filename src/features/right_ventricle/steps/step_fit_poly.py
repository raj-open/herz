#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


from collections.abc import Iterable

import numpy as np
import pandas as pd

from ....algorithms.anomalies import *
from ....algorithms.fitting.polynomials import *
from ....core.log import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.intervals import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_fit_poly",
    "step_refit_poly",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP fit polynomial-model to data", level=LOG_LEVELS.INFO)
def step_fit_poly(
    data: pd.DataFrame,
    quantity: str,
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    mode: EnumFittingMode,
    n_der: int,
    deg: int | None,
    intervals: Iterable[tuple[float, float]] = [(0, 1)],
) -> tuple[pd.DataFrame, list[tuple[Poly[float], tuple[int, int]]]]:
    """
    Fits polynomial to cycles in time-series, forcing certain conditions
    on the `n`th-derivatives at certain time points,
    and minimising wrt. the L²-norm.

    NOTE: Initial fitting runs from peak to peak.
    """
    # fit polynomial
    t = data["time"].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)
    cycles = data["cycle"].tolist()
    windows = cycles_to_windows(cycles)
    fits = fit_poly_cycles(t=t, x=x, windows=windows, conds=conds, deg=deg, intervals=intervals)

    # compute n'th derivatives
    data = compute_nth_derivatives_for_cycles(
        data, fits, quantity=quantity, n_der=n_der, mode=mode
    )

    return data, fits


@echo_function(
    message="STEP re-fit polynomial-model to data via interpolation", level=LOG_LEVELS.INFO
)
def step_refit_poly(
    data: pd.DataFrame,
    quantity: str,
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    mode: EnumFittingMode,
    n_der: int,
    period: float,
    deg: int | None,
    cfg: InterpConfigPoly,
    special: dict[str, SpecialPointsConfig],
) -> tuple[pd.DataFrame, list[tuple[Poly[float], tuple[int, int]]]]:
    """
    Re-fits polynomial to data series interpolating between certain special points.

    NOTE: assumes special points are normalised!
    """
    # compute environment
    t = {key: pt.time for key, pt in special.items()}
    x = {key: pt.value for key, pt in special.items()}
    env = {"T": period, "t": t, "x": x}
    for key, expr in cfg.points.items():
        env[key] = eval(expr, env)

    # determine the intervals (normalised)
    intervals = [(env[interval.root[0]], env[interval.root[1]]) for interval in cfg.intervals]
    intervals = collapse_intervals_to_cycle(intervals, period=period, offset=0, disjoint=True)
    # normalise
    intervals = [(t1 / period, t2 / period) for t1, t2 in intervals]

    # force conditions (use normalised time values)
    conds_ = []
    for key in cfg.special:
        # condition is n'th derivative is critical (=> n+1'th derivative = 0)
        pt = special[key]
        n = pt.spec.derivative
        cond = PolyDerCondition(derivative=n + 1, time=pt.time / period)
        conds_.append(cond)

    # NOTE: this results in an overfitted polynomial:
    # conds = conds + conds_ # include previous conditions

    # NOTE: this seems to be the correct way (and justifiably so):
    conds = conds_  # override previous conditions

    # run the fit method
    return step_fit_poly(data=data, quantity=quantity, conds=conds, mode=mode, n_der=n_der, deg=deg, intervals=intervals)  # fmt: skip


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
    """
    Computes the n'th derivatives of the fitted curve for each cycle.
    """
    t = data["time"].to_numpy(copy=True)

    match mode:
        case EnumFittingMode.AVERAGE:
            p, _ = fitsinfos[-1]
            fitsinfos = [(p, win) for _, win in fitsinfos[:-1]]
        case _:
            pass

    data[f"{quantity}[fit]"] = np.zeros(t.shape)
    for n in range(1, n_der + 1):
        data[f"d[{n},t]{quantity}[fit]"] = np.zeros(t.shape)

    # loop over all time-subintervals and compute the n'th derivatives
    for p, (i1, i2) in fitsinfos:
        tt = t[i1:i2]
        col = f"{quantity}[fit]"
        data[col][i1:i2] = p.values(tt)
        for n in range(1, n_der + 1):
            p = p.derivative()
            col = f"d[{n},t]{quantity}[fit]"
            data[col][i1:i2] = p.values(tt)

    return data
