#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.types import *

from ....core.log import *
from ....core.constants import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....queries.fitting import *
from ....algorithms.fitting.exponential import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_compute_pv_ees',
    'step_compute_pv_ea',
    'step_compute_pv_eed',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP compute "ees" from fitted P-V curve', level=LOG_LEVELS.INFO)
def step_compute_pv_ees(
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
):
    P_isomax = special_p['iso-max'].value
    P_es = special_p['es'].value
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value

    m = (P_isomax - P_es) / (V_ed - V_es)
    # V_0 = V_ed - P_isomax/m

    special_pv['ees'] = SpecialPointsConfigPV(
        name='ees',
        found=True,
        value=m,
        data=[
            # PointPV(pressure=0, volume=V_0),
            PointPV(pressure=P_es, volume=V_es),
            PointPV(pressure=P_isomax, volume=V_ed),
        ],
    )
    return


@echo_function(message='STEP compute "ea" from fitted P-V curve', level=LOG_LEVELS.INFO)
def step_compute_pv_ea(
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
):
    P_es = special_p['es'].value
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value

    m = P_es / (V_ed - V_es)

    special_pv['ea'] = SpecialPointsConfigPV(
        name='ea',
        found=True,
        value=m,
        data=[
            PointPV(pressure=0, volume=V_ed),
            PointPV(pressure=P_es, volume=V_es),
        ],
    )
    return


@echo_function(message='STEP compute "eed" from fitted P-V curve', level=LOG_LEVELS.INFO)
def step_compute_pv_eed(
    info_p: FittedInfo,
    info_v: FittedInfo,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
):
    poly_p = Poly[float](coeff=info_p.coefficients)
    poly_v = Poly[float](coeff=info_v.coefficients)

    t_edp = special_p['ed'].time
    t_edv = special_v['ed'].time

    P_ed = special_p['ed'].value
    V_ed = special_v['ed'].value

    dP = poly_p.derivative()
    dV = poly_v.derivative()

    m = dP(t_edp) / dV(t_edv)

    # compute intercept
    V_0 = V_ed - P_ed / m

    special_pv['eed'] = SpecialPointsConfigPV(
        name='eed',
        found=True,
        value=m,
        data=[
            PointPV(pressure=0, volume=V_0),
            PointPV(pressure=P_ed, volume=V_ed),
        ],
    )
    return
