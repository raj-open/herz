#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..setup.series import *
from ..core.poly import *
from ..models.enums import *
from ..models.user import *
from ..models.internal import *
from ..algorithms.cycles import *
from ..algorithms.fit import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_fit_curve',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_fit_curve(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
    init: bool,
    n_der: int = 2,
) -> tuple[pd.DataFrame, list[tuple[tuple[int, int], FittedInfo]]]:
    '''
    Fits polynomial to cycles in time-series, forcing certain conditions
    on the `n`th-derivatives at certain time points,
    and minimising wrt. the L²-norm.

    NOTE: Initial fitting runs from peak to peak.
    '''
    cfg = case.process
    conds = get_polynomial_condition(quantity, init=init)

    # fit polynomial
    t = data['time'].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)
    cycles = data['cycle'].tolist()
    fitinfos = fit_poly_cycles(t=t, x=x, cycles=cycles, conds=conds)

    # compute n'th derivatives
    data = compute_nth_derivatives_for_cycles(
        case, data, fitinfos, quantity=quantity, n_der=n_der
    )

    return data, fitinfos


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def compute_nth_derivatives_for_cycles(
    case: UserCase,
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
    n_der: int,
) -> pd.DataFrame:
    '''
    Computes the n'th derivatives of the fitted curve for each cycle.
    '''
    cfg = case.process
    N = len(data)
    t = data['time'].to_numpy(copy=True)

    match cfg.fit.mode:
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
            coeff = coeffs[k]
            # get drift-values:
            T, c, m, s = get_normalisation_params(info)
            # scale time
            tt = (t[i1:i2] - t[i1]) / T
            # compute nth-derivative of fitted polynom to normalise cycle
            if n > 0:
                coeff = get_derivative_coefficients(coeff)
                coeffs[k] = coeff
            xx = poly(tt, *coeff)
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
