#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.code import *
from ...thirdparty.misc import *

from ...core.log import *
from ...core.timing import *
from ...core.poly import *
from ...setup import config
from ...models.user import *
from ...models.app import *
from ...models.fitting import *
from ...models.user import *
from ...queries.fitting import *
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


def endpoint(case: RequestConfig):
    '''
    Processes right ventricular data
    '''
    # initialise timer + prog. meter
    prog = LogProgress(name=f'RUN CASE {case.label}', steps=5, logger=log_info)

    datas = dict()
    fitinfos = dict()
    points = dict()

    # set configs / settings
    cfg_poly = config.POLY
    mode_fit = case.process.fit.mode
    cfg_matching = config.MATCHING
    # for temporary alignment, to compute iso-max values
    cfg_matching_iso = MatchingConfig(pressure='min', volume='min')
    cfg_points = config.POINTS

    # process quantities separately
    for quantity, symb, cfg_data, shift in [
        ('pressure', 'P', case.data.pressure, 'peak'),
        ('volume', 'V', case.data.volume, 'peak'),
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

        subprog = prog.subtask(f'''INITIAL FIT CURVE {quantity}''', steps=1)
        conds = get_polynomial_condition(quantity, cfg=cfg_poly)
        data, fits = step_fit_curve(data, quantity=quantity, conds=conds, n_der=2, mode=mode_fit)
        subprog.next()

        subprog = prog.subtask(f'''INITIAL CLASSIFICATION OF POINTS {quantity}''', steps=1)
        points_data, points_fit = step_recognise_points(data, fitinfos=fits, quantity=quantity, cfg_points=cfg_points)  # fmt: skip
        subprog.next()

        subprog = prog.subtask(f'''COMPUTE ISO-MAX FOR {quantity}''', steps=2)
        data_, points_data_ = step_shift_data_custom(data, points=points_data, quantity=quantity, cfg_matching=cfg_matching_iso)  # fmt: skip
        subprog.next()
        step_iso_max(data_, points=points_data_, quantity=quantity)
        subprog.next()

        subprog = prog.subtask(f'''RE-ALIGN {quantity} FOR MATCHING''', steps=1)
        data, points_data = step_shift_data_custom(data, points=points_data, quantity=quantity, cfg_matching=cfg_matching)  # fmt: skip
        subprog.next()

        datas[quantity] = data
        fitinfos[quantity] = fits
        points[quantity] = points_fit
        prog.next()

    # process quantities separately
    for quantity, symb in [
        ('pressure', 'P'),
        ('volume', 'V'),
    ]:
        data = datas[quantity]
        fits = fitinfos[quantity]
        points_fit = points[quantity]

        subprog = prog.subtask(f'''OUTPUT TABLES {quantity}''', steps=1)
        step_output_single_table(case, data=data, quantity=quantity)
        subprog.next()

        subprog = prog.subtask('''OUTPUT TIME PLOTS''', steps=1)
        plt = step_output_time_plot(
            data=data,
            fitinfos=fits,
            points=points_fit,
            quantity=quantity,
            symb=symb,
            shifted=True,
            plot_name=case.name,
            plot_label=case.label,
            cfg_output=case.output,
            cfg_matching=cfg_matching,
        )
        # plt.show()
        subprog.next()
        prog.next()

    # combined output
    subprog = prog.subtask(f'''OUTPLOT P/V-LOOP PLOT''', steps=0)
    plt = step_output_loop_plot(
        data_p=datas['pressure'],
        fitinfos_p=fitinfos['pressure'],
        points_p=points['pressure'],
        data_v=datas['volume'],
        fitinfos_v=fitinfos['volume'],
        points_v=points['volume'],
        shifted=True,
        plot_name=case.name,
        plot_label=case.label,
        cfg_output=case.output,
        cfg_matching=cfg_matching,
    )
    # plt.show()
    subprog.next()

    return
