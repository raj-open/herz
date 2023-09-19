#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *
from ..thirdparty.physics import *
from ..thirdparty.system import *
from ..thirdparty.types import *

from ..setup import config
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_output_tables',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_tables(data: pd.DataFrame):
    cfg = config.OUTPUT_CONFIG
    cfg_units = config.UNITS

    path = cfg.table.path.__root__
    if not prepare_save_table(path=path):
        return

    cv_t = convert_units(unitFrom=cfg_units.time, unitTo=cfg.quantities.time.unit)
    cv_p = convert_units(unitFrom=cfg_units.pressure, unitTo=cfg.quantities.pressure.unit)
    cv_v = convert_units(unitFrom=cfg_units.volume, unitTo=cfg.quantities.volume.unit)

    table = pd.DataFrame(
        {
            'cycle': data['cycle'],
            'time': cv_t * data['time'],
            'pressure': cv_p * data['pressure'],
            'volume': cv_v * data['volume'],
        }
    ).astype(
        {
            'cycle': int,
            'time': float,
            'pressure': float,
            'volume': float,
        }
    )

    table.to_csv(
        path,
        sep=cfg.table.sep,
        decimal=cfg.table.decimal,
        na_rep='',
        header=[
            'cycle',
            cfg.quantities.time.name,
            cfg.quantities.pressure.name,
            cfg.quantities.volume.name,
        ],
        index=False,
        mode='w',
        encoding='utf-8',
        quotechar='"',
        doublequote=True,
    )

    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def prepare_save_table(path: Optional[str]) -> bool:
    if path is None:
        return False

    p = Path(os.path.dirname(path))
    p.mkdir(parents=True, exist_ok=True)
    return True
