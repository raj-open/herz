#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *

from ..setup import config
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_combine_data',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_combine_data(
    case: UserCase,
    data_pressure: pd.DataFrame,
    data_volume: pd.DataFrame,
) -> pd.DataFrame:
    cfg = case.process
    cfg_units = config.UNITS

    unit = cfg.combine.unit
    cv_t = convert_units(unitFrom=unit, unitTo=cfg_units.get('time', unit))

    time_pressure = data_pressure['time'].to_numpy(copy=True)
    pressure = data_pressure['pressure'].to_numpy(copy=True)
    time_volume = data_volume['time'].to_numpy(copy=True)
    volume = data_volume['volume'].to_numpy(copy=True)

    # get T_max
    T_max = cv_t * (cfg.combine.t_max or 0.0)
    T_max_p, _ = get_aspects(time_pressure)
    T_max_v, _ = get_aspects(time_volume)
    T_max = max(T_max, T_max_p, T_max_v)

    # compute num points and update T_max (ensure dt is as set)
    dt = cv_t * cfg.combine.dt
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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_aspects(t: np.ndarray) -> tuple[float, float]:
    dt = np.mean(np.diff(t))
    T_max = t[-1] - t[0] + dt
    return T_max, dt


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
