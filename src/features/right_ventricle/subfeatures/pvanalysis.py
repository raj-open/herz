#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *

from ....core.log import *
from ....setup import config
from ....models.polynomials import *
from ....models.fitting import *
from ..steps import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'subfeature_pv_series_steps',
    'subfeature_pv_fitting_steps',
    'subfeature_pv_recognition_steps',
]

# ----------------------------------------------------------------
# SUBFEATURES
# ----------------------------------------------------------------


def subfeature_pv_series_steps(
    prog: LogProgress,
    datas: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    subprog = prog.subtask(f'''INTERPOLATE P-V data sets''', steps=1)
    data_pv = step_interpolate_pv(
        data_p=datas['pressure'],
        data_v=datas['volume'],
    )
    subprog.next()
    prog.next()
    return data_pv


def subfeature_pv_fitting_steps(
    prog: LogProgress,
    data_pv: pd.DataFrame,
    infos: dict[str, FittedInfoNormalisation],
    polys: dict[str, Poly[float]],
    specials: dict[str, dict[str, SpecialPointsConfig]],
) -> tuple[FittedInfoExp, tuple[float, float], tuple[float, float]]:
    subprog = prog.subtask(f'''FIT EXP-CURVE TO P-V''', steps=1)
    fitinfo_exp = step_fit_exp(
        data=data_pv,
        info_p=infos['pressure'],
        info_v=infos['pressure'],
        poly_p=polys['pressure'],
        poly_v=polys['volume'],
        special_p=specials['pressure'],
        special_v=specials['volume'],
        cfg_fit=config.EXP,
    )
    subprog.next()
    prog.next()
    return fitinfo_exp


def subfeature_pv_recognition_steps(
    prog: LogProgress,
    fitinfos_trig: dict[str, tuple[FittedInfoTrig, list[tuple[float, float], list[tuple[float, float]]]]],
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    polys: dict[str, Poly[float]],
    specials: dict[str, dict[str, SpecialPointsConfig]],
):
    subprog = prog.subtask(f'''COMPUTE SPECIAL POINTS FOR P-V''', steps=1)
    specials['pv'] = step_compute_pv(
        poly_p=polys['pressure'],
        poly_v=polys['volume'],
        # fit_trig_p=fitinfos_trig['pressure'][0],
        # fit_trig_v=fitinfos_trig['volume'][0],
        fit_trig_p=None,
        fit_trig_v=None,
        fitinfo_exp=fitinfo_exp,
        special_p=specials['pressure'],
        special_v=specials['volume'],
        special_pv=specials['pv'],
    )
    subprog.next()
    prog.next()
    return
