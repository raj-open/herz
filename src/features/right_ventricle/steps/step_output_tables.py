#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.physics import *
from ....thirdparty.system import *
from ....thirdparty.types import *

from ....setup import config
from ....core.log import *
from ....models.user import *
from ....queries.scientific import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_output_single_table',
    'step_output_combined_table',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP output table for {quantity}', level=LOG_LEVELS.INFO)
def step_output_single_table(
    case: RequestConfig,
    data: pd.DataFrame,
    quantity: str,
    original_time: bool = True,
):
    path = case.output.table.path.root
    path = path.format(label=case.label, kind=f'{quantity}-time')
    if not prepare_save_table(path=path):
        return

    cv = output_conversions(case.output.quantities, units=config.UNITS)

    if original_time:
        data = data.sort_values(by=['time[orig]']).reset_index(drop=True)
        data['time'] = data['time[orig]']

    columns = list(data.columns)
    quantities = [col for col in case.output.quantities if col.key in columns]

    table = pd.DataFrame({col.key: cv[col.key] * data[col.key] for col in quantities}).astype(
        {col.key: col.type.value for col in quantities}
    )

    with open(path, 'w') as fp:
        sep = case.output.table.sep
        for header in [
            [col.name for col in quantities],
            [print_unit(col.unit, ascii=False) or '' for col in quantities],
        ]:
            fp.write(sep.join(header))
            fp.write('\n')

        table.to_csv(
            fp,
            sep=sep,
            decimal=case.output.table.decimal,
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


@echo_function(message='STEP output table for P + V', level=LOG_LEVELS.INFO)
def step_output_combined_table(
    case: RequestConfig,
    data: pd.DataFrame,
):
    path = case.output.table.path.root
    path = path.format(label=case.label, kind=f'combined')
    if not prepare_save_table(path=path):
        return

    cv = output_conversions(case.output.quantities, units=config.UNITS)

    table = pd.DataFrame(
        {col.key: cv[col.key] * data[col.key] for col in case.output.quantities if not col.ignore}
    ).astype({col.key: col.type.value for col in case.output.quantities if not col.ignore})

    table.to_csv(
        path,
        sep=case.output.table.sep,
        decimal=case.output.table.decimal,
        na_rep='',
        header=[col.name for col in case.output.quantities],
        index=False,
        mode='w',
        encoding='utf-8',
        quotechar='"',
        doublequote=True,
    )

    return


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def prepare_save_table(path: Optional[str]) -> bool:
    if path is None:
        return False

    p = Path(os.path.dirname(path))
    p.mkdir(parents=True, exist_ok=True)
    return True
