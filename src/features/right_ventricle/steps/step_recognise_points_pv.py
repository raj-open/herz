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
    poly_p: Poly[float],
    poly_v: Poly[float],
    fit_trig_p: FittedInfoTrig | None,
    fit_trig_v: FittedInfoTrig | None,
    fitinfo_exp: tuple[FittedInfoExp, tuple[float, float], tuple[float, float]],
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    special_pv: dict[str, SpecialPointsConfigPV],
) -> dict[str, SpecialPointsConfigPV]:
    '''
    Combines knowledge obtain from point recognition on the individual curves
    together with the fitted models
    in order to compute certain "special points" on the P-V curve.
    '''
    # get poly models
    dP_poly = poly_p.derivative()
    dV_poly = poly_v.derivative()

    # get trig models
    dP_osc = None
    dV_osc = None

    if isinstance(fit_trig_p, FittedInfoTrig):
        hshift = fit_trig_p.hshift
        hscale = fit_trig_p.hscale
        # vshift = fit_trig_p.vshift
        vscale = fit_trig_p.vscale
        drift = fit_trig_p.drift
        omega = 2 * pi / hscale
        # osc_p = lambda t: vshift + drift * t + vscale * math.cos(omega * (t - hshift))
        dP_osc = lambda t: drift - omega * vscale * math.sin(omega * (t - hshift))

    if isinstance(fit_trig_v, FittedInfoTrig):
        hshift = fit_trig_v.hshift
        hscale = fit_trig_v.hscale
        # vshift = fit_trig_v.vshift
        vscale = fit_trig_v.vscale
        drift = fit_trig_v.drift
        omega = 2 * pi / hscale
        # osc_v = lambda t: vshift + drift * t + vscale * math.cos(omega * (t - hshift))
        dV_osc = lambda t: drift - omega * vscale * math.sin(omega * (t - hshift))

    t_edp = special_p['ed'].time
    t_esp = special_p['es'].time
    P_ed = special_p['ed'].value
    P_es = special_p['es'].value
    P_iso = special_p['iso'].value
    P_min = special_p['dia'].value
    P_axis = min(P_min, 0)

    t_edv = special_v['ed'].time
    t_esv = special_v['es'].time
    V_ed = special_v['ed'].value
    V_es = special_v['es'].value
    V_iso = special_v['iso'].value

    if special_p['iso'].found:
        point = special_pv['piso']
        point.found = True
        point.value = P_iso
        point.data = [PointPV(pressure=P_iso, volume=V_ed)]

    if special_v['iso'].found:
        point = special_pv['viso']
        point.found = True
        point.value = V_iso
        point.data = [PointPV(pressure=P_ed, volume=V_iso)]

    match dP_osc, dV_osc:
        case None, None:
            m = (P_iso - P_es) / (V_ed - V_es)
        case _, None:
            m = dP_osc(t_esp) / dV_poly(t_esv)
        case None, _:
            m = dP_poly(t_esp) / dV_osc(t_esv)
        case _, _:
            m = dP_osc(t_esp) / dV_osc(t_esv)
    lin = lambda p: V_es + (p - P_es) / m
    V_0 = lin(0)
    V_1 = lin(P_iso)

    point = special_pv['ees']
    point.found = True
    point.value = m
    point.data = [
        PointPV(pressure=0, volume=V_0),
        PointPV(pressure=P_es, volume=V_es),
        PointPV(pressure=P_iso, volume=V_1),
    ]

    point = special_pv['V0']
    point.found = True
    point.value = V_0
    point.data = [
        PointPV(pressure=0, volume=V_0),
    ]

    point = special_pv['ea']
    point.found = True
    point.value = P_es / (V_ed - V_es)
    point.data = [
        PointPV(pressure=0, volume=V_ed),
        PointPV(pressure=P_es, volume=V_es),
    ]

    # compute gradient + intercept
    m = dP_poly(t_edp) / dV_poly(t_edv)
    V_axis = V_ed + (P_axis - P_ed) / m

    point = special_pv['eed-poly']
    point.found = True
    point.value = m
    point.data = [
        PointPV(pressure=P_axis, volume=V_axis),
        PointPV(pressure=P_ed, volume=V_ed),
    ]

    # compute eed via exp-fit
    fit_exp, (vmin, vmax), (pmin, pmax) = fitinfo_exp
    alpha = fit_exp.vshift
    beta = 1 / fit_exp.hscale
    m = beta * (pmax - alpha)
    V_axis = vmax + (P_axis - pmax) / m
    point = special_pv['eed-exp']
    point.found = True
    point.value = m
    point.data = [
        PointPV(pressure=P_axis, volume=V_axis),
        PointPV(pressure=P_ed, volume=V_ed),
    ]

    return special_pv
