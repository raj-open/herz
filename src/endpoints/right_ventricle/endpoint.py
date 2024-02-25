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
from ...models.user import *
from ...models.app import *
from ...models.fitting import *
from ...models.user import *
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


def endpoint(
    case: RequestConfig,
    cfg: AppConfig,
):
    '''
    Processes right ventricular data
    '''
    # initialise timer + prog. meter
    prog = LogProgress(name=f'RUN CASE {case.label}', steps=5, logger=log_info)

    datas = dict()
    fitinfos = dict()
    points = dict()

    # process quantities separately
    for quantity, symb, cfg_data, shift in [
        ('pressure', 'P', case.data.pressure, 'peak'),
        ('volume', 'V', case.data.volume, 'peak'),
    ]:
        subprog = prog.subtask(f'''READ DATA {quantity}''', steps=2)  # fmt: skip
        data = step_read_data(cfg=cfg, cfg_data=cfg_data, quantity=quantity)  # fmt: skip
        subprog.next()
        data = step_normalise_data(case, cfg=cfg, data=data, quantity=quantity)  # fmt: skip
        subprog.next()

        subprog = prog.subtask(f'''INITIAL RECOGNITION OF CYCLES {quantity} ({shift} -> {shift})''', steps=3)  # fmt: skip
        data = step_recognise_peaks(case, cfg=cfg, data=data, quantity=quantity)
        subprog.next()
        data = step_shift_data_extremes(case, cfg=cfg, data=data, quantity=quantity, shift=shift)  # fmt: skip
        subprog.next()
        data = step_recognise_cycles(case, cfg=cfg, data=data, quantity=quantity, shift=shift)  # fmt: skip
        subprog.next()

        subprog = prog.subtask(f'''INITIAL FIT CURVE {quantity}''', steps=1)  # fmt: skip
        data, fits = step_fit_curve(case, cfg=cfg, data=data, quantity=quantity)  # fmt: skip
        subprog.next()

        subprog = prog.subtask(f'''INITIAL CLASSIFICATION OF POINTS {quantity}''', steps=1)  # fmt: skip
        points_data, points_fit = step_recognise_points(case, cfg=cfg, data=data, fitinfos=fits, quantity=quantity)  # fmt: skip
        subprog.next()

        subprog = prog.subtask(f'''RE-ALIGN {quantity} FOR MATCHING''', steps=1)  # fmt: skip
        data, points_data = step_shift_data_custom(case, cfg=cfg, data=data, points=points_data, quantity=quantity)  # fmt: skip
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
        step_output_single_table(case, cfg=cfg, data=data, quantity=quantity)  # fmt: skip
        subprog.next()

        subprog = prog.subtask('''OUTPUT TIME PLOTS''', steps=1)
        plt = step_output_time_plot(case, cfg=cfg, data=data, fitinfos=fits, points=points_fit, quantity=quantity, symb=symb, shifted=True)  # fmt: skip
        # plt.show()
        subprog.next()
        prog.next()

    # combined output
    subprog = prog.subtask(f'''OUTPLOT P/V-LOOP PLOT''', steps=0)
    plt = step_output_loop_plot(
        case,
        cfg=cfg,
        data_p=datas['pressure'],
        fitinfos_p=fitinfos['pressure'],
        points_p=points['pressure'],
        data_v=datas['volume'],
        fitinfos_v=fitinfos['volume'],
        points_v=points['volume'],
        shifted=True,
    )
    # plt.show()
    subprog.next()

    return
