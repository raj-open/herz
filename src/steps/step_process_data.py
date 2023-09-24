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
) -> pd.DataFrame:
    cfg = config.PROCESS_CONFIG

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

    # detect 'bad' parts of cycles
    N = len(data)
    x = data[['pressure', 'volume']].to_numpy(copy=True)
    cycles = data['cycle'].tolist()
    marked = mark_pinched_points_on_cycles(x=x, cycles=cycles, sig_t=0.1)
    data['marked'] = marked

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
    data['time'] = np.linspace(start=0.0, stop=T, num=N, endpoint=False)

    return data


def step_fit_curve(
    data: pd.DataFrame,
    quantities: str,
    n_der: int = 2,
) -> pd.DataFrame:
    '''
    TODO: Check/correct the following assumptions!

    ## Assumptions on pressure-series ##

    `n = 2`, `h=7`.

    - Assume `P(0) = P(1) =` local maximum.
    - The `n`-th derivative `x⁽ⁿ⁾` is a polynomial,
      with `h` alternating peaks/troughs,
      whereby the two end points `0` and `T` are peaks.
    - This implies that the `(n+1)`-th derivative
      `P⁽ⁿ⁺¹⁾` is a polynomial
      with `h` zeros (and hence of degree `h`),
      two of which are the end points.

    So `P` is a polynomial of degree `n + h + 1`.
    Force conditions:

    - `P(0) = P(1)`;
    - `P´(0) = 0`; `P´(1) = 0`;
    - `P⁽ⁿ⁺¹⁾(0) = 0`; `P⁽ⁿ⁺¹⁾(1) = 0`;

    ## Assumptions on volume-series ##

    `n = 1`, `h=7`.

    - Assume `V(0) = V(1)`.
    - The `n`-th derivative `x⁽ⁿ⁾` is a polynomial,
      with `h` alternating peaks/troughs,
      whereby the two end points `0` and `T` are peaks.
    - This implies that the `(n+1)`-th derivative
      `V⁽ⁿ⁺¹⁾` is a polynomial
      with `h` zeros (and hence of degree `h`),
      two of which are the end points.

    So `V` is a polynomial of degree `n + h + 1`.
    Force conditions:

    - `V(0) = V(1)`;;
    '''
    cfg = config.PROCESS_CONFIG

    t = data['time'].to_numpy(copy=True)
    cycles = data['cycle'].tolist()

    # determine start and end of each cycle
    windows = cycles_to_windows(cycles)

    for quantity in quantities:
        x = data[quantity].to_numpy(copy=True)

        deg = 2
        opt = []
        match quantity:
            case 'pressure':
                n = 2
                h = 7  # number of 'humps' of n-th derivative of x
                deg = h + n + 1
                opt = [
                    (0, 0.0),
                    (0, 1.0),
                    (1, 0.0),
                    (1, 1.0),
                    (n + 1, 0.0),
                    (n + 1, 1.0),
                ]
            case 'volume':
                n = 1
                h = 7  # number of 'humps' of n-th derivative of x
                deg = h + n + 1
                opt = [
                    (0, 0.0),
                    (0, 1.0),
                ]

        # fit polynomial
        mode_average = cfg.fit.mode == EnumFittingMode.AVERAGE
        x, coeffs = fit_poly_cycles(
            t=t,
            x=x,
            cycles=cycles,
            deg=deg,
            opt=opt,
            average=mode_average,
        )
        data[f'{quantity}[fit]'] = x

        # compute derivatives
        for i in range(1, n_der + 1):
            for k, (i1, i2) in enumerate(windows):
                if not mode_average or k == 0:
                    coeffs[k] = derivative_coefficients(coeffs[k])
                coeff = coeffs[0] if mode_average else coeffs[k]
                tt, T = normalise_to_unit_interval(t[i1:i2])
                x[i1:i2] = 1 / T * poly(tt, *coeff)

            data[f'd[{i},t]{quantity}[fit]'] = x

    return data
