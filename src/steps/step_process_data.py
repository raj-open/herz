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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_compute_extremes',
    'step_recognise_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_compute_extremes(data: pd.DataFrame, quantities: list[str]) -> pd.DataFrame:
    N = len(data)
    for quantity in quantities:
        values = data[quantity]
        peaks, troughs = get_extremes(values)
        data[f'{quantity}_peak'] = where_to_characteristic(peaks, N)
        data[f'{quantity}_trough'] = where_to_characteristic(troughs, N)
    return data


def step_recognise_cycles(
    data: pd.DataFrame,
    quantity: str,
    reduce: bool = True,
    remove_gaps: bool = True,
) -> pd.DataFrame:
    N = len(data)
    peaks = characteristic_to_where(data[f'{quantity}_peak'])
    x = data[['pressure', 'volume']].to_numpy(copy=True)
    # only perform if there is 1 cycle:
    data['marked'] = (
        mark_pinched_points_on_cycles(x=x, peaks=peaks, sig_t=0.1)
        if len(peaks) <= 2
        else [False] * N
    )
    # peaks = characteristic_to_where(data[f'{quantity}_peak'])
    cycles = get_cycles(peaks=peaks, N=N, remove_gaps=remove_gaps)
    data['cycle'] = cycles
    if reduce:
        data = data[cycles >= 0]
    return data
