#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from .thirdparty.misc import *

from .core.log import *
from .core.poly import *
from .setup import config
from .models.internal import *
from .steps import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def enter(path: str, *_):
    LP = LogProgress('''SETUP''')
    config.set_user_config(path)
    LP.next()

    for case in config.CASES:
        datas = dict()
        fitinfos = dict()
        points = dict()
        LP = LogProgress(f'''RUN CASE {case.label}''', steps=5)

        # process quantities separately
        for quantity, symb, cfg_data, shift in [
            ('pressure', 'P', case.data.pressure, 'peak'),
            ('volume', 'V', case.data.volume, 'peak'),
        ]:
            LPsub = LP.subtask(f'''READ DATA {quantity}''', 2)
            data = step_read_data(cfg_data, quantity)
            LPsub.next()
            data = step_normalise_data(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''INITIAL RECOGNITION OF CYCLES {quantity} ({shift} -> {shift})''', 4)  # fmt: skip
            data = step_recognise_peaks(case, data, quantity=quantity)
            LPsub.next()
            data = step_shift_data_extremes(case, data, quantity=quantity, shift=shift)
            LPsub.next()
            data = step_recognise_cycles(case, data, quantity=quantity, shift=shift)
            LPsub.next()
            if case.process.cycles.remove_bad:
                data = step_removed_marked_sections(case, data)
            LPsub.next()

            LPsub = LP.subtask(f'''INITIAL FIT CURVE {quantity}''', 1)
            data, fits = step_fit_curve(case, data, quantity=quantity, init=True)
            LPsub.next()

            LPsub = LP.subtask(f'''INITIAL CLASSIFICATION OF POINTS {quantity}''', 1)
            points_data, points_fit = step_recognise_points(case, data, fits, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''RE-RECOGNITION OF CYCLES {quantity} / MATCHING''', 1)
            data = step_shift_data_custom(case, data, points_data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''RE-FIT CURVE {quantity}''', 1)
            data, fits = step_fit_curve(case, data, quantity=quantity, init=False)
            LPsub.next()

            LPsub = LP.subtask(f'''RE-CLASSIFICATION OF POINTS {quantity}''', 1)
            _, points_fit = step_recognise_points(case, data, fits, quantity=quantity)
            LPsub.next()

            datas[quantity] = data
            fitinfos[quantity] = fits
            points[quantity] = points_fit
            LP.next()

        # process quantities separately
        for quantity, symb in [
            ('pressure', 'P'),
            ('volume', 'V'),
        ]:
            data = datas[quantity]
            fits = fitinfos[quantity]
            points_fit = points[quantity]

            LPsub = LP.subtask(f'''OUTPUT TABLES {quantity}''', 1)
            step_output_single_table(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask('''OUTPUT TIME PLOTS''', 1)
            plt = step_output_time_plot(
                case, data, fits, points_fit, quantity=quantity, symb=symb
            )
            # plt.show()
            LPsub.next()
            LP.next()

        # combined output
        LPsub = LP.subtask(f'''OUTPLOT P/V-LOOP PLOT''', 0)
        plt = step_output_loop_plot(
            case,
            data_p=datas['pressure'],
            fitinfos_p=fitinfos['pressure'],
            points_p=points['pressure'],
            data_v=datas['volume'],
            fitinfos_v=fitinfos['volume'],
            points_v=points['volume'],
        )
        # plt.show()
        LPsub.next()
        LP.next()
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SECONDARY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXCEUTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    # sys.tracebacklimit = 0
    args = sys.argv[1:]
    enter(*args)
