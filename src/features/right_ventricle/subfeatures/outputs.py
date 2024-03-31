#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *

from ....core.log import *
from ....setup import config
from ....models.polynomials import *
from ....models.user import *
from ....models.fitting import *
from ..steps import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'subfeature_output_steps',
]

# ----------------------------------------------------------------
# SUBFEATURES
# ----------------------------------------------------------------


def subfeature_output_steps(
    prog: LogProgress,
    case: RequestConfig,
    datas: dict[str, pd.DataFrame],
    data_pv: pd.DataFrame,
    infos: dict[str, FittedInfoNormalisation],
    polys: dict[str, Poly[float]],
    fitinfos_trig: dict[
        str,
        tuple[
            Poly[float] | None,
            list[tuple[float, float]],
            list[tuple[float, float]],
        ],
    ],
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    specials: dict[str, dict[str, SpecialPointsConfig]],
):
    subprog = prog.subtask(f'''OUTPUT SPECIAL POINTS''', steps=1)
    step_output_special_points(
        case,
        special_p=specials['pressure'],
        special_v=specials['volume'],
        special_pv=specials['pv'],
        info_p=infos['pressure'],
        info_v=infos['volume'],
        fitinfos_trig_p=fitinfos_trig['pressure'],
        fitinfos_trig_v=fitinfos_trig['volume'],
        cfg_trig_p=config.TRIG.pressure,
        cfg_trig_v=config.TRIG.volume,
        fitinfo_exp=fitinfo_exp,
    )
    subprog.next()
    prog.next()

    # process quantities separately
    for quantity, symb in [
        ('pressure', 'P'),
        ('volume', 'V'),
    ]:
        subprog = prog.subtask(f'''OUTPUT TABLES {quantity}''', steps=1)
        step_output_single_table(case, data=datas[quantity], quantity=quantity)
        subprog.next()

        subprog = prog.subtask('''OUTPUT TIME PLOTS''', steps=1)
        step_output_time_plot(
            data=datas[quantity],
            info=infos[quantity],
            poly=polys[quantity],
            fitinfo_trig=fitinfos_trig[quantity],
            special=specials[quantity],
            quantity=quantity,
            symb=symb,
            plot_title=case.title,
            plot_label=case.label,
            cfg_output=case.output,
        )
        subprog.next()
        prog.next()

    # combined output
    subprog = prog.subtask(f'''OUTPLOT P/V-LOOP PLOT''', steps=1)
    step_output_loop_plot(
        data_p=datas['pressure'],
        data_v=datas['volume'],
        data_pv=data_pv,
        info_p=infos['pressure'],
        info_v=infos['volume'],
        poly_p=polys['pressure'],
        poly_v=polys['volume'],
        fitinfo_trig_p=fitinfos_trig['pressure'],
        fitinfo_trig_v=fitinfos_trig['volume'],
        fitinfo_exp=fitinfo_exp,
        special_p=specials['pressure'],
        special_v=specials['volume'],
        special_pv=specials['pv'],
        plot_title=case.title,
        plot_label=case.label,
        cfg_output=case.output,
    )
    subprog.next()
    prog.next()

    return
