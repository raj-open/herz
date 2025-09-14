#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


from typing import Callable
from typing import Optional

import numpy as np
import pandas as pd

from ....core.log import *
from ....core.utils import *
from ....models.app import *
from ....models.user import *
from ....setup import config
from ....thirdparty.maths import *
from ....thirdparty.physics import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_read_data",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP read data from csv", level=LOG_LEVELS.INFO)
def step_read_data(
    case: RequestConfig,
    cfg: DataTimeSeries,
    quantity: str,
) -> pd.DataFrame:
    unit_time: str = config.UNITS.get("time", "s")
    unit_quantity: str = config.UNITS[quantity]

    path = cfg.path.root
    data = pd.read_csv(
        path,
        sep=cfg.sep,
        decimal=cfg.decimal,
        skiprows=(get_bool_function(cfg.skip) if isinstance(cfg.skip, str) else cfg.skip),
    )
    t = get_column(data, unit=unit_time, cfg=cfg.time)
    x = get_column(data, unit=unit_quantity, cfg=cfg.value)

    data = pd.DataFrame(
        {
            "time": t,
            quantity: x,
        }
    ).astype(
        {
            "time": float,
            quantity: float,
        }
    )
    data.sort_values(inplace=True, by=["time"])
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
        raise KeyError(f"{key} not found in data set with columns {', '.join(columns)}")

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

            except Exception as _:
                return False

    except Exception as _:
        return lambda i: False
