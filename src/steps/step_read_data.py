#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.code import *
from ..thirdparty.data import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.types import *

from ..setup import config
from ..core.utils import *
from ..models.app import *
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_read_data',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_read_data(case: UserCase) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = case.data
    cfg_units = config.UNITS

    data_pressure = get_data_from_csv(
        quantity='pressure',
        unit_time=cfg_units.get('time', 's'),
        unit_quantity=cfg_units.get('pressure', 'Pa'),
        config=cfg.pressure,
    )

    data_volume = get_data_from_csv(
        quantity='volume',
        unit_time=cfg_units.get('time', 's'),
        unit_quantity=cfg_units.get('volume', 'm^3'),
        config=cfg.volume,
    )

    return data_pressure, data_volume


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_data_from_csv(
    quantity: str,
    unit_time: str,
    unit_quantity: str,
    config: DataTimeSeries,
) -> pd.DataFrame:
    path = config.path.__root__
    data = pd.read_csv(
        path,
        sep=config.sep,
        decimal=config.decimal,
        skiprows=get_bool_function(configk.skip)
        if isinstance(config.skip, str)
        else config.skip,
    )
    t = get_column(data, unit=unit_time, config=config.time)
    x = get_column(data, unit=unit_quantity, config=config.value)

    data = pd.DataFrame(
        {
            'time': t,
            quantity: x,
        }
    ).astype(
        {
            'time': float,
            quantity: float,
        }
    )

    return data


def get_column(
    data: pd.DataFrame,
    config: DataTypeQuantity,
    unit: Optional[str] = None,
) -> np.asarray:
    col = data[config.name][:]
    X = np.asarray(col, dtype=config.type.value)
    if config.unit is not None and unit is not None:
        cv = convert_units(unitFrom=config.unit, unitTo=unit)
        X = cv * X
    return X


def get_bool_function(text: str) -> Callable[[int], bool]:
    try:
        fct_ = eval(text)

        def fct(i: int) -> bool:
            try:
                return fct_(i)
            except:
                return False

    except:
        return lambda i: False
