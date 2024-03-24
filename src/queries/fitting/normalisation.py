#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.data import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...models.fitting import *
from ...models.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_normalisation_params',
    'get_normalised_data',
    'get_unnormalised_data',
    'get_unnormalised_fit_trig',
    'get_unnormalised_point',
    'get_unnormalised_polynomial',
    'get_unnormalised_polynomial_time_only',
    'get_unnormalised_polynomial_values_only',
    'get_unnormalised_special',
    'get_unnormalised_time',
]

# ----------------------------------------------------------------
# METHODS - ONB
# ----------------------------------------------------------------


def get_normalisation_params(
    info: FittedInfo,
) -> list[float, float, float, float]:
    params = info.normalisation
    T = params.period
    c = params.intercept
    m = params.gradient
    s = params.scale
    return T, c, m, s


def get_unnormalised_time(
    t: float,
    info: FittedInfo,
) -> float:
    T = info.normalisation.period
    t = T * (t % 1)
    return t


def get_unnormalised_point(
    t: float,
    x: float,
    info: FittedInfo,
) -> tuple[float, float]:
    T, c, m, s = get_normalisation_params(info)
    t = T * (t % 1)
    x = (c + m * t) + s * x
    return t, x


def get_unnormalised_polynomial(
    info: FittedInfo,
) -> Poly:
    '''
    Normalisation:
    ```
    z(t) = (x(t₀ + T·t) - (c + mt))/s
    ```
    Unnormalisation (but write polynomial centred on `t₀` instead of `0`):
    ```
    x(t) = c + m/T · (t-t₀) + s · z((t-t₀)/T)
    ```
    '''
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    deg = len(coeff) - 1
    Tpow = np.cumprod([1] + [T] * deg)
    coeff_rescaled = [s * cc / TT for cc, TT in zip(coeff, Tpow)]
    coeff_rescaled[0] += c
    coeff_rescaled[1] += m / T
    return Poly(coeff=coeff_rescaled)


def get_unnormalised_polynomial_time_only(
    info: FittedInfo,
) -> Poly:
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    deg = len(coeff) - 1
    Tpow = np.cumprod([1] + [T] * deg)
    coeff_rescaled = [s * cc / TT for cc, TT in zip(coeff, Tpow)]
    return Poly(coeff=coeff_rescaled)


def get_unnormalised_polynomial_values_only(
    info: FittedInfo,
) -> Poly:
    '''
    Normalisation:
    ```
    z(t) = (x(t₀ + T·t) - (c + mt))/s
    ```
    Unnormalisation that restores the shape of the the polynomial only,
    but does not re-scale time and values.
    ```
    x(T·t)/s = c/s + m/s · (t – t₀) + z(t – t₀)
    ```
    '''
    coeff = info.coefficients
    T, c, m, s = get_normalisation_params(info)
    coeff_rescaled = coeff[:]
    coeff_rescaled[0] += c / (s or 1.0)
    coeff_rescaled[1] += m / (s or 1.0)
    return Poly(coeff=coeff_rescaled)


def get_unnormalised_data(
    data: pd.DataFrame,
    infos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
    t_split: float = 0.0,
    renormalise: bool = True,
) -> pd.DataFrame:
    '''
    Undoes normalisation of the data series.
    If `renormalise=True` is set,
    then renormalises using commmon parameters.
    '''
    t_new = []
    dt_new = []
    x_new = []
    t = data['time'].to_numpy(copy=True)
    x = data[quantity].to_numpy(copy=True)

    # get common parameters
    if renormalise:
        _, info = infos[-1]
        T0, c0, m0, s0 = get_normalisation_params(info)
    else:
        T0, c0, m0, s0 = 1, 0, 0, 1

    # un- and renormalise all cycles
    for (i1, i2), info in infos[:-1]:
        T, c, m, s = get_normalisation_params(info)
        # normalise time and points for cycle
        # NOTE: normalise t, then x!
        tt = (t[i1:i2] - t[i1]) / T
        xx = x[i1:i2]
        xx = (xx - (c + m * tt)) / s
        # renormalise based on common parameters
        # NOTE: renormalise x, then t!
        xx = c0 + m0 * tt + s0 * xx
        tt = T0 * tt
        # determine time-increments
        dt = np.diff(tt)
        dt = np.concatenate([dt, [dt[-1]]])
        # store
        t_new += tt.tolist()
        dt_new += dt.tolist()
        x_new += xx.tolist()

    # split times
    t_new = np.asarray(t_new)
    t = t_new + T0 * (t_new < t_split) - t_split

    # store in new data structure
    data = pd.DataFrame(
        {
            'time[orig]': t_new,
            'time': t,
            'dt': dt_new,
            quantity: x_new,
        }
    ).astype(
        {
            'time[orig]': 'float',
            'time': 'float',
            'dt': 'float',
            quantity: 'float',
        }
    )
    return data


def get_normalised_data(
    data: pd.DataFrame,
    infos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
    t_split: float = 0.0,
) -> pd.DataFrame:
    '''
    Normalises data series.
    '''
    data = get_unnormalised_data(
        data,
        infos=infos,
        quantity=quantity,
        t_split=t_split,
        renormalise=False,
    )
    data = data[['time', 'dt', quantity]]
    data = data.rename(columns={quantity: 'value'})
    return data


def get_unnormalised_special(
    special: dict[str, SpecialPointsConfig],
    info: FittedInfo,
    key_align: str,
):
    '''
    Renormalises (without realignment) + adds the alignment time.
    '''
    point = special[key_align]
    t_align = get_unnormalised_time(point.time, info=info)
    for _, point in special.items():
        t, x = point.time, point.value
        t, x = get_unnormalised_point(t, x, info=info)
        point.time = t
        point.value = x
    special['align'] = SpecialPointsConfig(
        name='align',
        ignore=True,
        time=t_align,
    )
    return special


def get_unnormalised_fit_trig(
    fit: FittedInfoTrig,
    info: FittedInfo,
) -> FittedInfoTrig:
    '''
    The model
    ```
    f(t) = a + b·(t - t₀) + r·cos(ω·t - φ)
    ```
    is first unnormalised to
    ```
    g(t) = C + m·t + f(t)
        = (C + s·a) + m
    ```
    '''
    T, c, m, s = get_normalisation_params(info)
    return FittedInfoTrig(
        hshift=T * fit.hshift,
        hscale=T * fit.hscale,
        vshift=c + s * fit.vshift,
        vscale=s * fit.vscale,
        drift=m + s * fit.drift,
    )
