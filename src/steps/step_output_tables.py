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
    'step_output_single_table',
    'step_output_combined_table',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_output_single_table(
    case: UserCase,
    data: pd.DataFrame,
    quantity: str,
    original_time: bool = True,
):
    cfg = case.output

    path = cfg.table.path.__root__
    path = path.format(label=case.label, kind=f'{quantity}-time')
    if not prepare_save_table(path=path):
        return

    cv = output_conversions(cfg.quantities)

    if original_time:
        data = data.sort_values(by=['time[orig]']).reset_index(drop=True)
        data['time'] = data['time[orig]']

    columns = list(data.columns)
    quantities = [col for col in cfg.quantities if col.key in columns]

    table = pd.DataFrame({col.key: cv[col.key] * data[col.key] for col in quantities}).astype(
        {col.key: col.type.value for col in quantities}
    )

    with open(path, 'w') as fp:
        sep = cfg.table.sep
        for header in [
            [col.name for col in quantities],
            [print_unit(col.unit, ascii=False) or '' for col in quantities],
        ]:
            fp.write(sep.join(header))
            fp.write('\n')

        table.to_csv(
            fp,
            sep=sep,
            decimal=cfg.table.decimal,
            na_rep='',
            header=None,
            # header=[col.name for col in quantities],
            index=False,
            mode='w',
            encoding='utf-8',
            quotechar='"',
            doublequote=True,
            # float_format='%.6f',
        )

    return


def step_output_combined_table(
    case: UserCase,
    data: pd.DataFrame,
):
    cfg = case.output

    path = cfg.table.path.__root__
    path = path.format(label=case.label, kind=f'combined')
    if not prepare_save_table(path=path):
        return

    cv = output_conversions(cfg.quantities)

    table = pd.DataFrame(
        {col.key: cv[col.key] * data[col.key] for col in cfg.quantities}
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
