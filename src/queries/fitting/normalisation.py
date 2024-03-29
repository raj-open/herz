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
    'get_unnormalised_data',
    'get_unnormalised_trig',
    'get_unnormalised_point',
    'get_unnormalised_polynomial',
    'get_unnormalised_special',
    'get_unnormalised_time',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_unnormalised_time(
    t: float,
    info: FittedInfoNormalisation,
) -> float:
    T = info.period
    t = T * (t % 1)
    return t


def get_unnormalised_point(
    t: float,
    x: float,
    info: FittedInfoNormalisation,
) -> tuple[float, float]:
    T, c, m, s = get_normalisation_params(info)
    t = T * (t % 1)
    x = (c + m * t) + s * x
    return t, x


def get_unnormalised_polynomial(
    fit: FittedInfoPoly,
    info: FittedInfoNormalisation,
) -> Poly[float]:
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
    coeff = fit.coefficients
    p = Poly[float](coeff=coeff)
    T, c, m, s = get_normalisation_params(info)
    return Poly[float](coeff=[c, m]) + s * p.rescale(a=1 / T)


def get_unnormalised_trig(
    fit: FittedInfoTrig,
    info: FittedInfoNormalisation,
) -> FittedInfoTrig:
    '''
    The model
    ```
    f(t) = a + b·t + r·cos(ω·(t - t₀))
    ```
    is unnormalised to
    ```
    g(t) = C + m·t + s·f(t/T)
         = (C + s·a) + (m + s·b/T)·t + s·r·cos(ω/T·(t - t₀·T))
    ```
    '''
    T, c, m, s = get_normalisation_params(info)
    return FittedInfoTrig(
        hshift=T * fit.hshift,
        hscale=T * fit.hscale,
        vshift=c + s * fit.vshift,
        vscale=s * fit.vscale,
        # NOTE: this remains 0 if m and fit.drift are 0
        drift=m + s * fit.drift / T,
    )


def get_unnormalised_data(
    data: pd.DataFrame,
    infos: list[tuple[tuple[int, int], FittedInfoNormalisation]],
    quantity: str,
    n_der: int = 0,
    renormalise: bool = True,
) -> pd.DataFrame:
    '''
    Undoes normalisation of the data series.
    If `renormalise=True` is set,
    then renormalises using commmon parameters.
    '''
    data['dt'] = 0

    # get common parameters
    _, fit0 = infos[-1]

    # un/renormalise all cycles - incl. fitted models
    for (i1, i2), fit in infos[:-1]:
        T, c, m, s = get_normalisation_params(fit0 if renormalise else fit)
        tt = data['time'][i1:i2]
        xx = data[quantity][i1:i2]

        tt = T * tt
        xx = c + m * tt + s * xx

        data['time'][i1:i2] = tt
        data[quantity][i1:i2] = xx

        for n in range(n_der + 1):
            match n:
                case 0:
                    col = f'{quantity}[fit]'
                    xx = data[col][i1:i2]
                    xx = c + m * tt + s * xx
                case 1:
                    col = f'd[{n},t]{quantity}[fit]'
                    xx = data[col][i1:i2]
                    xx = m + s * xx
                case _:
                    col = f'd[{n},t]{quantity}[fit]'
                    xx = data[col][i1:i2]
                    xx = s * xx
            data[col][i1:i2] = xx

    return data


def get_unnormalised_special(
    special: dict[str, SpecialPointsConfig],
    info: FittedInfoNormalisation,
):
    '''
    Renormalises (without realignment) + adds the alignment time.
    '''
    for _, point in special.items():
        t, x = point.time, point.value
        t, x = get_unnormalised_point(t, x, info=info)
        point.time = t
        point.value = x
    return special


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def get_normalisation_params(
    info: FittedInfoNormalisation,
) -> tuple[float, float, float, float]:
    T = info.period
    c = info.intercept
    m = info.gradient
    s = info.scale
    return T, c, m, s
