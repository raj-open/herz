#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.code import *
from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.physics import *
from ....thirdparty.types import *

from ....setup import config
from ....core.utils import *
from ....models.app import *
from ....models.user import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_read_data',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def step_read_data(
    cfg: AppConfig,
    cfg_data: DataTimeSeries,
    quantity: str,
) -> pd.DataFrame:
    cfg_units = cfg.settings.units

    unit_time: str = cfg_units.get('time', 's')
    unit_quantity: str = cfg_units.get(quantity)

    path = cfg_data.path.root
    data = pd.read_csv(
        path,
        sep=cfg_data.sep,
        decimal=cfg_data.decimal,
        skiprows=(
            get_bool_function(cfg_data.skip)
            if isinstance(cfg_data.skip, str)
            else cfg_data.skip
        ),
    )
    t = get_column(data, unit=unit_time, cfg=cfg_data.time)
    x = get_column(data, unit=unit_quantity, cfg=cfg_data.value)

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


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


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
