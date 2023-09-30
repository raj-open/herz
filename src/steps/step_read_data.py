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


def step_read_data(
    cfg: DataTimeSeries,
    quantity: str,
) -> pd.DataFrame:
    cfg_units = config.UNITS

    unit_time: str = cfg_units.get('time', 's')
    unit_quantity: str = cfg_units.get(quantity)

    path = cfg.path.__root__
    data = pd.read_csv(
        path,
        sep=cfg.sep,
        decimal=cfg.decimal,
        skiprows=get_bool_function(cfg.skip) if isinstance(cfg.skip, str) else cfg.skip,
    )
    t = get_column(data, unit=unit_time, cfg=cfg.time)
    x = get_column(data, unit=unit_quantity, cfg=cfg.value)

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
    data.sort_values(inplace=True, by=['time'])
    data.reset_index(inplace=True, drop=True)

    return data


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_column(
    data: pd.DataFrame,
    cfg: DataTypeQuantity,
    unit: Optional[str] = None,
) -> np.asarray:
    key = cfg.name
    try:
        col = data[key][:]
    except KeyError as e:
        columns = list(data.columns)
        raise KeyError(f'{key} not found in data set with columns {", ".join(columns)}')

    X = np.asarray(col, dtype=cfg.type.value)
    if cfg.unit is not None and unit is not None:
        cv = convert_units(unitFrom=cfg.unit, unitTo=unit)
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
