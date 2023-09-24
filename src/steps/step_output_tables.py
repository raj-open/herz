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
from ..setup.conversion import *
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


def step_output_tables(
    case: UserCase,
    data: pd.DataFrame,
):
    cfg = case.output
    cfg_units = config.UNITS

    path = cfg.table.path.__root__
    if not prepare_save_table(path=path):
        return

    cv = output_conversions(cfg.quantities)

    table = pd.DataFrame(
        {col.key: getattr(cv, col.key, 1) * data[col.key] for col in cfg.quantities}
    ).astype({col.key: col.type.value for col in cfg.quantities})
    table.to_csv(
        path,
        sep=cfg.table.sep,
        decimal=cfg.table.decimal,
        na_rep='',
        header=[col.name for col in cfg.quantities],
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
