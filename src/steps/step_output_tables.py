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
    # s = cv_t
    s = 1.0

    columns = [
        (
            'cycle',
            'cycle',
            'float',
            data['cycle'],
        ),
        (
            'time',
            cfg.quantities.time.name,
            'float',
            cv_t * data['time'],
        ),
        (
            'pressure',
            cfg.quantities.pressure.name,
            'float',
            cv_p * data['pressure'],
        ),
        (
            'pressure[fit]',
            f'{cfg.quantities.pressure.name}[fit]',
            'float',
            cv_p * data['pressure[fit]'],
        ),
        (
            'd[1,t]pressure[fit]',
            'd[1,t]P[fit]',
            'float',
            (cv_p / s) * data['d[1,t]pressure[fit]'],
        ),
        (
            'd[2,t]pressure[fit]',
            'd[2,t]P[fit]',
            'float',
            (cv_p / s**2) * data['d[2,t]pressure[fit]'],
        ),
        (
            'volume',
            cfg.quantities.volume.name,
            'float',
            cv_v * data['volume'],
        ),
        (
            'volume[fit]',
            f'{cfg.quantities.volume.name}[fit]',
            'float',
            cv_p * data['volume[fit]'],
        ),
        (
            'd[1,t]volume[fit]',
            'd[1,t]V[fit]',
            'float',
            (cv_p / s) * data['d[1,t]volume[fit]'],
        ),
        (
            'd[2,t]V[fit]',
            'd[2,t]volume[fit]',
            'float',
            (cv_p / s**2) * data['d[2,t]volume[fit]'],
        ),
    ]

    table = pd.DataFrame({key: x for (key, name, unit, x) in columns}).astype(
        {key: unit for (key, name, unit, x) in columns}
    )
    table.to_csv(
        path,
        sep=cfg.table.sep,
        decimal=cfg.table.decimal,
        na_rep='',
        header=[name for (key, name, unit, x) in columns],
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
