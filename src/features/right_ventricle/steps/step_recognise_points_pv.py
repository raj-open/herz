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
    'step_compute_pv',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP compute special points from fitted P-V curve', level=LOG_LEVELS.INFO)
def step_compute_pv(
    info_p: FittedInfo,
    info_v: FittedInfo,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
) -> dict[str, SpecialPointsConfigPV]:
    special_pv = {}

    poly_p = Poly[float](coeff=info_p.coefficients)
    poly_v = Poly[float](coeff=info_v.coefficients)
    dP = poly_p.derivative()
    dV = poly_v.derivative()

    t_edp = special_p['ed'].time
    P_ed = special_p['ed'].value
    P_es = special_p['es'].value
    P_isomax = special_p['iso-max'].value

    t_edv = special_v['ed'].time
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value

    special_pv['ees'] = SpecialPointsConfigPV(
        name='ees',
        found=True,
        value=(P_isomax - P_es) / (V_ed - V_es),
        data=[
            # PointPV(pressure=0, volume=V_0),
            PointPV(pressure=P_es, volume=V_es),
            PointPV(pressure=P_isomax, volume=V_ed),
        ],
    )

    special_pv['ea'] = SpecialPointsConfigPV(
        name='ea',
        found=True,
        value=P_es / (V_ed - V_es),
        data=[
            PointPV(pressure=0, volume=V_ed),
            PointPV(pressure=P_es, volume=V_es),
        ],
    )

    # compute gradient + intercept
    m = dP(t_edp) / dV(t_edv)
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

    return special_pv
