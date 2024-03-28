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
    prog = LogProgress(name=f'RUN CASE {case.label}', steps=10, logger=log_info)

    # set configs / settings
    datas = dict()
    infos = dict()
    fits_trig = dict()
    cfg_points = config.POINTS.model_copy(deep=True)
    specials = {
        'pressure': cfg_points.pressure,
        'volume': cfg_points.volume,
        'pv': cfg_points.pv,
    }
    dataparts = dict()
    mode_fit = case.process.fit.mode

    for quantity, symb, shift, cfg_data, conds, cfg_points, cfg_trig, key_align in [
        (
            'pressure',
            'P',
            'peak',
            case.data.pressure,
            config.POLY.pressure,
            specials['pressure'],
            config.TRIG.pressure,
            config.MATCHING.pressure,
        ),
        (
            'volume',
            'V',
            'peak',
            case.data.volume,
            config.POLY.volume,
            specials['volume'],
            config.TRIG.volume,
            config.MATCHING.volume,
        ),
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
        data, fitinfos = step_fit_poly(data, quantity=quantity, conds=conds, n_der=2, mode=mode_fit)
        _, info = fitinfos[-1]
        subprog.next()

        subprog = prog.subtask(f'''RECOGNISE CRITICAL POINTS OF {quantity} VIA POLY-FITTING''', steps=1)
        special, points_data = step_recognise_points(data, fitinfos=fitinfos, special=cfg_points)
        subprog.next()

        subprog = prog.subtask(f'''RENORMALISE DATA + POLY-FITTING FOR {quantity}''', steps=3)
        data = get_unnormalised_data(data, infos=fitinfos, quantity=quantity)
        subprog.next()
        p = get_unnormalised_polynomial(info)
        info.coefficients = p.coefficients
        subprog.next()
        # NOTE: just renormalises, but does not realign.
        special = get_unnormalised_special(special, info=info, key_align=key_align)
        subprog.next()

        if cfg_trig is not None:
            subprog = prog.subtask(f'''FIT TRIG-CURVE + COMPUTE ISO-MAX FOR {quantity}''', steps=2)
            data_anon = data.rename(columns={quantity: 'value'})
            T, offset = info.normalisation.period, 0
            fit_trig, intervals = step_fit_trig(data_anon, p, offset=offset, period=T, special=special, cfg_fit=cfg_trig, symb=symb)  # fmt: skip
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

    subprog = prog.subtask(f'''FIT EXP-CURVE TO P-V''', steps=1)
    step_fit_exp(
        data_p=datas['pressure'],
        data_v=datas['volume'],
        info_p=infos['pressure'],
        info_v=infos['pressure'],
        special_p=specials['pressure'],
        special_v=specials['volume'],
        cfg_fit=config.EXP,
    )
    subprog.next()
    prog.next()

    subprog = prog.subtask(f'''COMPUTE SPECIAL POINTS FOR P-V''', steps=1)
    specials['pv'] = step_compute_pv(
        info_p=infos['pressure'],
        info_v=infos['volume'],
        special_p=specials['pressure'],
        special_v=specials['volume'],
        special_pv=specials['pv'],
    )
    subprog.next()
    prog.next()

    for quantity in ['pressure', 'volume']:
        points_data = dataparts[quantity]
        data = datas[quantity]

        subprog = prog.subtask(f'''RE-ALIGN {quantity} FOR MATCHING''', steps=1)
        data = step_shift_data_custom(data, points_data, key_align=key_align)
        subprog.next()

        datas[quantity] = data
        prog.next()

    subprog = prog.subtask(f'''OUTPUT SPECIAL POINTS FOR {quantity}''', steps=1)
    step_output_special_points(
        case,
        special_p=specials['pressure'],
        special_v=specials['volume'],
        special_pv=specials['pv'],
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
        special_pv=specials['pv'],
        plot_name=case.name,
        plot_label=case.label,
        cfg_output=case.output,
    )
    subprog.next()
    prog.next()

    return
