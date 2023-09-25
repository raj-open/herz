#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..core.utils import *
from ..core.poly import *
from ..models.user import *
from ..algorithms.peaks import *
from ..algorithms.cycles import *
from ..algorithms.bad_points import *
from ..algorithms.fit import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_compute_extremes',
    'step_recognise_cycles',
    'step_removed_marked_sections',
    'step_fit_curve',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_compute_extremes(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
) -> pd.DataFrame:
    N = len(data)
    values = data[quantity]
    peaks, troughs = get_extremes(values)
    data[f'{quantity}[peak]'] = where_to_characteristic(peaks, N)
    data[f'{quantity}[trough]'] = where_to_characteristic(troughs, N)
    return data


def step_recognise_cycles(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
    remove_gaps: bool = True,
) -> pd.DataFrame:
    cfg = case.process

    # compute time increment for later
    N = len(data)
    t = data['time'].to_numpy(copy=True)
    dt = (t[-1] - t[0]) / (N - 1)

    # get cycles based on peaks
    N = len(data)
    peaks = characteristic_to_where(data[f'{quantity}[peak]'])
    cycles = get_cycles(peaks=peaks, N=N, remove_gaps=remove_gaps)
    data['cycle'] = cycles
    data = data[data['cycle'] >= 0]

    # # detect 'bad' parts of cycles
    # N = len(data)
    # x = data[['pressure', 'volume']].to_numpy(copy=True)
    # cycles = data['cycle'].tolist()
    # marked = mark_pinched_points_on_cycles(x=x, cycles=cycles, sig_t=0.1)
    # data['marked'] = marked
    N = len(data)
    data['marked'] = [False] * N

    # shift data to peak-to-peak:
    peaks = characteristic_to_where(data[f'{quantity}[peak]'])
    if len(peaks) > 0:
        index_max = max(peaks)
        indices = list(range(N))
        indices = indices[index_max:] + indices[:index_max]
        data = data.iloc[indices, :]
        data.reset_index(inplace=True, drop=True)
        s = N - 1 - index_max
        peaks = [s + i for i in peaks]

    # recompute time axis.
    # NOTE: we assume that time has already been homogenised.
    N = len(data)
    T = N * dt
    data['time'] = np.linspace(start=0.0, stop=T, num=N, endpoint=False)

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


def step_fit_curve(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
    n_der: int = 2,
) -> tuple[pd.DataFrame, list[float]]:
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
    x, coeffs = fit_poly_cycles(
        t=t,
        x=x,
        cycles=cycles,
        deg=cfg_poly.degree,
        conds=cfg_poly.conditions,
        average=mode_average,
    )
    data[f'{quantity}[fit]'] = x

    # compute derivatives
    for n in range(1, n_der + 1):
        for k, (i1, i2) in enumerate(windows):
            if not mode_average or k == 0:
                coeffs[k] = derivative_coefficients(coeffs[k])
            coeff = coeffs[0] if mode_average else coeffs[k]
            # scale time
            tt, T = normalise_to_unit_interval(t[i1:i2])
            # remove drift
            c, m, s, _ = normalise_interpolated_drift(tt, x[i1:i2], T=1)
            # compute normalised derivative
            dnx = poly(tt, *coeff)
            # undo effects of time-scaling + drift-removal
            x[i1:i2] = ((m if n == 1 else 0.0) + s * dnx) / T

        data[f'd[{n},t]{quantity}[fit]'] = x

    return data, coeffs[0]
