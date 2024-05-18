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
from ....queries.fitting import *
from ..steps import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'subfeature_time_series_steps',
]

# ----------------------------------------------------------------
# SUBFEATURES
# ----------------------------------------------------------------


def subfeature_time_series_steps(
    prog: LogProgress,
    case: RequestConfig,
    datas: dict[str, pd.DataFrame],
    dataparts: dict[str, list[tuple[tuple[int, int], dict[str, int]]]],
    infos: dict[str, FittedInfoNormalisation],
    polys: dict[str, Poly[float]],
    interpols_poly: dict[str, Poly[float] | None],
    interpols_trig: dict[str, tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]]],
    specials: dict[str, dict[str, SpecialPointsConfig]],
):
    for quantity, symb, shift, cfg_data, conds, cfg_points, cfg_poly, cfg_trig, key_align in [
        (
            'pressure',
            'P',
            'peak',
            case.data.pressure,
            config.POLY.pressure,
            specials['pressure'],
            None if config.iPOLY is None else config.iPOLY.pressure,
            None if config.iTRIG is None else config.iTRIG.pressure,
            config.MATCHING.pressure,
        ),
        (
            'volume',
            'V',
            'peak',
            case.data.volume,
            config.POLY.volume,
            specials['volume'],
            None if config.iPOLY is None else config.iPOLY.volume,
            None if config.iTRIG is None else config.iTRIG.volume,
            config.MATCHING.volume,
        ),
    ]:
        subfeature_time_series_steps_single(
            prog=prog,
            case=case,
            datas=datas,
            dataparts=dataparts,
            infos=infos,
            polys=polys,
            interpols_poly=interpols_poly,
            interpols_trig=interpols_trig,
            specials=specials,
            quantity=quantity,
            symb=symb,
            shift=shift,
            cfg_data=cfg_data,
            conds=conds,
            cfg_points=cfg_points,
            cfg_poly=cfg_poly,
            cfg_trig=cfg_trig,
            key_align=key_align,
        )
    return


def subfeature_time_series_steps_single(
    prog: LogProgress,
    case: RequestConfig,
    datas: dict[str, pd.DataFrame],
    dataparts: dict[str, list[tuple[tuple[int, int], dict[str, int]]]],
    infos: dict[str, FittedInfoNormalisation],
    polys: dict[str, Poly[float]],
    interpols_poly: dict[str, Poly[float] | None],
    interpols_trig: dict[str, tuple[FittedInfoTrig | None, list[tuple[float, float]], list[tuple[float, float]]]],
    specials: dict[str, dict[str, SpecialPointsConfig]],
    quantity: str,
    symb: str,
    shift: bool,
    cfg_data: DataTimeSeries,
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    cfg_points: dict[str, SpecialPointsConfig],
    cfg_poly: InterpConfigPoly | None,
    cfg_trig: InterpConfigTrig | None,
    key_align: str,
):
    subprog = prog.subtask(f'''READ DATA {quantity}''', steps=2)
    data = step_read_data(case, cfg=cfg_data, quantity=quantity)
    subprog.next()
    data = step_clean_cycles(case, data=data, quantity=quantity)
    subprog.next()

    subprog = prog.subtask(f'''RECOGNISE CYCLES {quantity} ({shift} -> {shift})''', steps=3)
    data = step_recognise_peaks(data, quantity=quantity)
    subprog.next()
    data = step_shift_data_extremes(data, quantity=quantity, shift=shift)
    subprog.next()
    data = step_recognise_cycles(data, quantity=quantity, shift=shift)
    subprog.next()

    subprog = prog.subtask(f'''NORMALISE DATA {quantity}''', steps=2)
    data, infos_ = step_normalise(data=data, quantity=quantity)
    info, _ = infos_[-1]
    subprog.next()

    subprog = prog.subtask(f'''FIT POLY-CURVE FOR {quantity}''', steps=1)
    conf_ = case.process.fit
    data, fitsinfos_poly = step_fit_poly(data, quantity=quantity, conds=conds, n_der=2, mode=conf_.mode)
    poly, _ = fitsinfos_poly[-1]
    subprog.next()

    subprog = prog.subtask(f'''RECOGNISE CRITICAL POINTS OF {quantity} VIA POLY-FITTING''', steps=1)
    special, points_data = step_recognise_points(data, fitinfos=fitsinfos_poly, cfg=cfg_points, key_align=key_align)
    subprog.next()

    interp_poly = None
    # if cfg_poly is not None:
    #     # TODO
    #     cfg_poly.interval
    #     subprog = prog.subtask(f'''INTERPOLATE POLY-CURVE + COMPUTE ISO-MAX FOR {quantity}''', steps=2)
    #     data_anon = data.rename(columns={quantity: 'value'})
    #     interp_poly = step_interp_poly(data_anon, special=special, cfg_poly=cfg_poly, symb=symb)  # fmt: skip

    #     conf_ = case.process.fit
    #     data, fitsinfos_poly = step_refit_poly(data, quantity=quantity, conds=conds, n_der=2, mode=conf_.mode)
    #     poly, _ = fitsinfos_poly[-1]
    #     # special, points_data = step_recognise_points(data, fitinfos=fitsinfos_poly, cfg=cfg_points, key_align=key_align)
    #     subprog.next()
    #     # special = step_recognise_iso(interp_poly, special=special)
    #     # subprog.next()

    interp_trig = None
    hull_trig = []
    intervals_trig = []
    if cfg_trig is not None:
        subprog = prog.subtask(f'''INTERPOLATE TRIG-CURVE + COMPUTE ISO-MAX FOR {quantity}''', steps=2)
        data_anon = data.rename(columns={quantity: 'value'})
        interp_trig, hull_trig, intervals_trig = step_interp_trig(data_anon, poly=poly, special=special, cfg_fit=cfg_trig, symb=symb)  # fmt: skip
        subprog.next()
        special = step_recognise_iso(interp_trig, special=special)
        subprog.next()

    subprog = prog.subtask(f'''RENORMALISE DATA + FITTINGS FOR {quantity}''', steps=4)
    data = get_unnormalised_data(data, infos=infos_, quantity=quantity, renormalise=True)
    subprog.next()
    # NOTE: just renormalises, but does not realign.
    special = get_unnormalised_special(special, info=info)
    subprog.next()
    poly = get_unnormalised_polynomial(poly, info=info)
    subprog.next()
    if interp_trig is not None:
        T = info.period
        interp_trig = get_unnormalised_trig(interp_trig, info=info)
        hull_trig = [(T * a, T * b) for a, b in hull_trig]
        intervals_trig = [(T * a, T * b) for a, b in intervals_trig]
    subprog.next()

    subprog = prog.subtask(f'''RE-ALIGN {quantity} FOR MATCHING''', steps=4)
    data = step_shift_data_custom(data, points_data)
    subprog.next()
    special = get_realignment_special(special, info=info)
    subprog.next()
    poly = get_realignment_polynomial(poly, special=special)
    subprog.next()
    if interp_trig is not None:
        interp_trig = get_realignment_trig(interp_trig, special=special)
        hull_trig = get_realignment_intervals(hull_trig, info=info, special=special, collapse=False)
        intervals_trig = get_realignment_intervals(intervals_trig, info=info, special=special, collapse=False)
    subprog.next()

    datas[quantity] = data
    dataparts[quantity] = points_data
    infos[quantity] = info
    polys[quantity] = poly
    interpols_poly[quantity] = interp_poly
    interpols_trig[quantity] = (interp_trig, hull_trig, intervals_trig)
    specials[quantity] = special
    prog.next()
    return
