#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *

from ..setup import config
from ..core.poly import *
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
    n_der: int = 2,
) -> tuple[pd.DataFrame, list[FittedInfo]]:
    '''
    Fits polynomial to cycles in time-series,
    forcing certain conditions on the `n`th-derivatives
    at certain time points,
    and minimising wrt. the L²-norm.
    '''
    cfg = case.process
    cfg_poly = config.POLY[quantity]

    t = data['time'].to_numpy(copy=True)
    cycles = data['cycle'].tolist()

    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    # fit polynomial
    x = data[quantity].to_numpy(copy=True)
    mode_average = cfg.fit.mode == EnumFittingMode.AVERAGE
    infos = fit_poly_cycles(
        t=t,
        x=x,
        cycles=cycles,
        deg=cfg_poly.degree,
        conds=cfg_poly.conditions,
        average=mode_average,
    )

    # compute derivatives
    if mode_average:
        coeff = infos[-1].coefficients
        coeffs = [coeff[:] for _ in windows]
    else:
        coeffs = [coeff[:] for coeff, _, _, _, _ in infos]
    for n in range(n_der + 1):
        # loop over all time-subintervals:
        for k, (i1, i2) in enumerate(windows):
            # get coefficients for (n-1)th derivative polynomial for cycle k:
            coeff = coeffs[k]
            # get drift-values:
            T, c, m, s = get_normalisation_params(infos[k])
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

    return data, infos
