#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *

from ..setup import config
from ..core.utils import *
from ..algorithms.peaks import *
from ..algorithms.cycles import *
from ..algorithms.fit import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_compute_extremes',
    'step_recognise_cycles',
    'step_fit_curve',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_compute_extremes(data: pd.DataFrame, quantities: list[str]) -> pd.DataFrame:
    N = len(data)
    for quantity in quantities:
        values = data[quantity]
        peaks, troughs = get_extremes(values)
        data[f'{quantity}[peak]'] = where_to_characteristic(peaks, N)
        data[f'{quantity}[trough]'] = where_to_characteristic(troughs, N)
    return data


def step_recognise_cycles(
    data: pd.DataFrame,
    quantity: str,
    remove_gaps: bool = True,
    remove_piched: bool = True,
) -> pd.DataFrame:
    N = len(data)

    # get cycles based on peaks
    peaks = characteristic_to_where(data[f'{quantity}[peak]'])
    cycles = get_cycles(peaks=peaks, N=N, remove_gaps=remove_gaps)
    data['cycle'] = cycles
    data = data[data['cycle'] >= 0]

    # detect 'bad' parts of cycles
    x = data[['pressure', 'volume']].to_numpy(copy=True)
    data['marked'] = (
        mark_pinched_points_on_cycles(x=x, cycles=cycles, sig_t=0.1)
        if len(peaks) <= 2
        else [False] * N
    )
    if remove_piched:
        data = data[data['marked'] == False]

    return data


def step_fit_curve(
    data: pd.DataFrame,
    quantity: str,
    n_der: int = 2,
) -> pd.DataFrame:
    t = data['time'].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)
    cycles = data['cycle'].tolist()

    # fit polynomial
    x, coeffs = fit_poly_right_ventricular_pressure_cycles(t=t, x=x, cycles=cycles)
    data[f'{quantity}[fit]'] = x

    # compute derivatives
    for i in range(1, n_der + 1):
        x, coeffs = fit_poly_nth_derivative(t, coeffs=coeffs, cycles=cycles)
        data[f'd[{i},t]{quantity}[fit]'] = x

    return data
