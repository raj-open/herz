#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.code import *
from ...thirdparty.maths import *
from ...thirdparty.misc import *

from ...core.log import *
from ...core.timing import *
from ...setup import config
from ...models.app import *
from ...models.polynomials import *
from ...models.user import *
from ...models.fitting import *
from ...queries.fitting import *
from ...queries.scientific import *
from .steps import *

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
    prog = LogProgress(name=f'RUN CASE {case.label}', steps=9, logger=log_info)

    datas = dict()
    infos = dict()
    fits_trig = dict()
    specials = dict()
    dataparts = dict()

    # set configs / settings
    cfg_poly = config.POLY
    mode_fit = case.process.fit.mode
    cfg_matching = config.MATCHING
    cfg_points = config.POINTS
    cfg_trig = config.TRIG

    for quantity, symb, cfg_data, cfg_trig_, shift in [
        ('pressure', 'P', case.data.pressure, cfg_trig.pressure, 'peak'),
        ('volume', 'V', case.data.volume, cfg_trig.volume, 'peak'),
    ]:
        subprog = prog.subtask(f'''READ DATA {quantity}''', steps=2)
        data = step_read_data(case, cfg=cfg_data, quantity=quantity)
        subprog.next()
        data = step_normalise_data(case, data=data, quantity=quantity)
        subprog.next()

        subprog = prog.subtask(f'''INITIAL RECOGNITION OF CYCLES {quantity} ({shift} -> {shift})''', steps=3)
        data = step_recognise_peaks(data, quantity=quantity)
        subprog.next()
        data = step_shift_data_extremes(data, quantity=quantity, shift=shift)
        subprog.next()
        data = step_recognise_cycles(data, quantity=quantity, shift=shift)
        subprog.next()

        subprog = prog.subtask(f'''FIT POLY-CURVE FOR {quantity}''', steps=1)
        conds = get_polynomial_condition(quantity, cfg=cfg_poly)
        data, fitinfos = step_fit_poly(data, quantity=quantity, conds=conds, n_der=2, mode=mode_fit)
        _, info = fitinfos[-1]
        subprog.next()

        subprog = prog.subtask(f'''RECOGNISE CRITICAL POINTS OF {quantity} VIA POLY-FITTING''', steps=1)
        settings = get_point_settings(quantity, cfg=cfg_points)
        special, points_data = step_recognise_points(data, fitinfos=fitinfos, special=settings)
        subprog.next()

        subprog = prog.subtask(f'''RENORMALISE DATA + POLY-FITTING FOR {quantity}''', steps=3)
        data = get_unnormalised_data(data, infos=fitinfos, quantity=quantity)
        subprog.next()
        p = get_unnormalised_polynomial(info)
        info.coefficients = p.coefficients
        subprog.next()
        # NOTE: just renormalises, but does not realign.
        key_align = get_alignment_point(quantity, cfg=cfg_matching)
        special = get_unnormalised_special(special, info=info, key_align=key_align)
        subprog.next()

        if cfg_trig_ is not None:
            subprog = prog.subtask(f'''FIT TRIG-CURVE + COMPUTE ISO-MAX FOR {quantity}''', steps=2)
            data_anon = data.rename(columns={quantity: 'value'})
            T, offset = info.normalisation.period, 0
            fit_trig, intervals = step_fit_trig(data_anon, p, offset=offset, period=T, special=special, cfg_trig=cfg_trig_, symb=symb)  # fmt: skip
            subprog.next()
            special = step_recognise_iso_max(fit_trig, special=special)
            info_trig = (fit_trig, intervals)
            subprog.next()
        else:
            info_trig = None

        datas[quantity] = data
        dataparts[quantity] = points_data
        infos[quantity] = info
        fits_trig[quantity] = info_trig
        specials[quantity] = special
        prog.next()

    subprog = prog.subtask(f'''FIT EXP-CURVE TO P-V''', steps=3)
    step_fit_exp_pressure()
    subprog.next()
    step_fit_exp_volume()
    subprog.next()
    step_fit_exp_pv()
    subprog.next()
    prog.next()

    for quantity in ['pressure', 'volume']:
        points_data = dataparts[quantity]
        data = datas[quantity]

        subprog = prog.subtask(f'''RE-ALIGN {quantity} FOR MATCHING''', steps=1)
        data = step_shift_data_custom(data, points_data, quantity=quantity, cfg_matching=cfg_matching)
        subprog.next()

        datas[quantity] = data
        prog.next()

    subprog = prog.subtask(f'''OUTPUT SPECIAL POINTS FOR {quantity}''', steps=1)
    step_output_special_points(
        case,
        special_p=specials['pressure'],
        special_v=specials['volume'],
        fit_trig_p=(fits_trig['pressure'] or (None, None))[0],
        fit_trig_v=(fits_trig['volume'] or (None, None))[0],
        info_p=infos['pressure'],
        info_v=infos['volume'],
    )
    subprog.next()
    prog.next()

    # process quantities separately
    for quantity, symb in [
        ('pressure', 'P'),
        ('volume', 'V'),
    ]:
        subprog = prog.subtask(f'''OUTPUT TABLES {quantity}''', steps=1)
        step_output_single_table(case, data=data, quantity=quantity)
        subprog.next()

        subprog = prog.subtask('''OUTPUT TIME PLOTS''', steps=1)
        step_output_time_plot(
            data=datas[quantity],
            info=infos[quantity],
            fits_trig=fits_trig[quantity],
            special=specials[quantity],
            quantity=quantity,
            symb=symb,
            plot_name=case.name,
            plot_label=case.label,
            cfg_output=case.output,
        )
        subprog.next()
        prog.next()

    # combined output
    subprog = prog.subtask(f'''OUTPLOT P/V-LOOP PLOT''', steps=1)
    step_output_loop_plot(
        data_p=datas['pressure'],
        info_p=infos['pressure'],
        special_p=specials['pressure'],
        data_v=datas['volume'],
        info_v=infos['volume'],
        special_v=specials['volume'],
        plot_name=case.name,
        plot_label=case.label,
        cfg_output=case.output,
    )
    subprog.next()
    prog.next()

    return
