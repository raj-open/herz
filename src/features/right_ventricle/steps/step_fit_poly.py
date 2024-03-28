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
) -> tuple[pd.DataFrame, list[tuple[tuple[int, int], FittedInfo]]]:
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
    fitinfos = fit_poly_cycles(t=t, x=x, windows=windows, conds=conds)

    # compute n'th derivatives
    data = compute_nth_derivatives_for_cycles(data, fitinfos, quantity=quantity, n_der=n_der, mode=mode)

    return data, fitinfos


@echo_function(message='STEP refit polynomial-model to data', level=LOG_LEVELS.INFO)
def step_refit_poly(
    data: pd.DataFrame,
    quantity: str,
    points: dict[str, SpecialPointsConfig],
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    n_der: int,
    mode: EnumFittingMode,
    key_align: str,
) -> tuple[pd.DataFrame, list[tuple[tuple[int, int], FittedInfo]]]:
    '''
    Refits polynomials, by additionally forcing derivative conditions
    of previously determined special points to be retained.
    '''
    # add in conditions for special points
    # NOTE: only used special pts marked for reuse
    conds = conds[:] + [
        PolyDerCondition(derivative=point.spec.derivative + 1, time=point.time)
        for _, point in points.items()
        if point.spec is not None
        # and (point.spec.reuse or key == key_align)
        and point.spec.reuse
    ]

    # shift current conditions
    t_align = points[key_align].time if key_align in points else 0.0
    conds = shift_conditions(conds, t0=t_align)

    data, fitinfos = step_fit_poly(
        data=data,
        quantity=quantity,
        conds=conds,
        n_der=n_der,
        mode=mode,
    )

    return data, fitinfos


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def compute_nth_derivatives_for_cycles(
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
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
            _, info_av = fitinfos[-1]
            coeffs = [info_av.coefficients[:] for _, _ in fitinfos[:-1]]
        case _:
            coeffs = [info.coefficients[:] for _, info in fitinfos[:-1]]

    # compute each n'th derivative
    for n in range(n_der + 1):
        x = np.zeros((N,), dtype=float)
        # loop over all time-subintervals:
        for k, ((i1, i2), info) in enumerate(fitinfos[:-1]):
            # get coefficients for (n-1)th derivative polynomial for cycle k:
            p = Poly[float](coeff=coeffs[k])
            # get drift-values:
            T, c, m, s = get_normalisation_params(info)
            # scale time
            tt = (t[i1:i2] - t[i1]) / T
            # compute nth-derivative of fitted polynom to normalise cycle
            if n > 0:
                p = p.derivative()
                coeffs[k] = p.coefficients
            xx = p.values(tt)

            # undo effects of time-scaling and drift-removal
            # NOTE: from 2nd derivative onwards, drift-removal has no effect)
            match n:
                case 0:
                    x[i1:i2] = c + m * tt + s * xx
                case 1:
                    x[i1:i2] = (m + s * xx) / T
                case _:
                    x[i1:i2] = s * xx / T
        # store fitted results
        match n:
            case 0:
                data[f'{quantity}[fit]'] = x
            case _:
                data[f'd[{n},t]{quantity}[fit]'] = x

    return data
