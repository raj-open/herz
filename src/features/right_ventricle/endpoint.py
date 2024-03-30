#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...core.log import *
from ...setup import config
from ...models.user import *
from .steps import *
from .subfeatures import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'endpoint',
]

# ----------------------------------------------------------------
# MAIN METHODS - ENDPOINT
# ----------------------------------------------------------------


@echo_function(tag='FEATURE {feature.value}', level=LOG_LEVELS.INFO)
def endpoint(feature: EnumEndpoint, case: RequestConfig):
    '''
    Processes right ventricular data
    '''
    prog = LogProgress(name=f'RUN CASE {case.label}', steps=8, logger=log_info)

    # set configs / settings
    datas = dict()
    infos = dict()
    polys = dict()
    fitinfos_trig = dict()
    cfg_points = config.POINTS.model_copy(deep=True)
    specials = {
        'pressure': cfg_points.pressure,
        'volume': cfg_points.volume,
        'pv': cfg_points.pv,
    }
    dataparts = dict()

    # process time-series
    subfeature_time_series_steps(
        prog=prog,
        case=case,
        datas=datas,
        dataparts=dataparts,
        infos=infos,
        polys=polys,
        fitinfos_trig=fitinfos_trig,
        specials=specials,
    )

    # pv analysis
    data_pv = subfeature_pv_series_steps(prog=prog, datas=datas)
    fitinfo_exp = subfeature_pv_fitting_steps(
        prog=prog,
        data_pv=data_pv,
        infos=infos,
        polys=polys,
        specials=specials,
    )
    subfeature_pv_recognition_steps(
        prog=prog,
        fitinfos_trig=fitinfos_trig,
        fitinfo_exp=fitinfo_exp,
        polys=polys,
        specials=specials,
    )

    # perform output steps
    subfeature_output_steps(
        prog=prog,
        case=case,
        datas=datas,
        data_pv=data_pv,
        infos=infos,
        polys=polys,
        fitinfos_trig=fitinfos_trig,
        fitinfo_exp=fitinfo_exp,
        specials=specials,
    )
    return
