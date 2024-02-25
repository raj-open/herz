#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.physics import *

from ....setup import config
from ....models.app import *
from ....models.user import *
from .methods import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_normalise_data',
    'step_combine_data',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def step_normalise_data(
    case: RequestConfig,
    data: pd.DataFrame,
    quantity: str,
) -> pd.DataFrame:
    unit = case.process.combine.unit
    cv_t = convert_units(unitFrom=unit, unitTo=config.UNITS.get('time', unit))

    time = data['time'].to_numpy(copy=True)
    time = time - min(time)
    values = data[quantity].to_numpy(copy=True)

    # get total duration
    N, dt, T = get_time_aspects(time)
    T = max(T, cv_t * (case.process.combine.t_max or 0.0))

    # compute num points and update T (ensure dt is as set)
    dt = cv_t * case.process.combine.dt or dt
    N = math.ceil(T / dt)
    T = N * dt

    # interpolate data
    time_uniform = np.linspace(start=0, stop=T, num=N, endpoint=False)
    values = interpolate_curve(time_uniform, x=time, y=values, T_max=T, periodic=True)

    data = pd.DataFrame({'time': time_uniform, quantity: values}).astype(
        {'time': float, quantity: float}
    )

    return data


def step_combine_data(
    case: RequestConfig,
    data_pressure: pd.DataFrame,
    data_volume: pd.DataFrame,
) -> pd.DataFrame:
    unit = case.process.combine.unit
    cv_t = convert_units(unitFrom=unit, unitTo=config.UNITS.get('time', unit))

    time_pressure = data_pressure['time'].to_numpy(copy=True)
    pressure = data_pressure['pressure'].to_numpy(copy=True)
    time_volume = data_volume['time'].to_numpy(copy=True)
    volume = data_volume['volume'].to_numpy(copy=True)

    # get T_max
    T_max = cv_t * (case.process.combine.t_max or 0.0)
    _, _, T_max_p = get_time_aspects(time_pressure)
    _, _, T_max_v = get_time_aspects(time_volume)
    T_max = max(T_max, T_max_p, T_max_v)

    # compute num points and update T_max (ensure dt is as set)
    dt = cv_t * case.process.combine.dt
    N = math.ceil(T_max / dt)
    T_max = N * dt

    # interpolate data
    time = np.linspace(start=0, stop=T_max, num=N, endpoint=False)
    pressure = interpolate_curve(time, x=time_pressure, y=pressure, T_max=T_max, periodic=True)
    volume = interpolate_curve(time, x=time_volume, y=volume, T_max=T_max, periodic=True)

    data = pd.DataFrame(
        {
            'time': time,
            'pressure': pressure,
            'volume': volume,
        }
    ).astype(
        {
            'time': float,
            'pressure': float,
            'volume': float,
        }
    )

    return data


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def interpolate_curve(
    t: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    T_max: float,
    periodic: bool,
) -> np.ndarray:
    return np.interp(
        t,
        x,
        y,
        left=None,
        right=None,
        period=T_max if periodic else None,
    )
