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
        LP = LogProgress(f'''RUN CASE {case.label}''', steps=6)

        # process quantities separately
        for quantity, symb, cfg_data, ext in [
            ('pressure', 'P', case.data.pressure, 'peak'),
            ('volume', 'V', case.data.volume, 'peak'),
        ]:
            LPsub = LP.subtask(f'''READ DATA {quantity}''', 2)
            data = step_read_data(cfg_data, quantity)
            LPsub.next()
            data = step_normalise_data(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''RECOGNISE CYCLES {quantity}''', 2)
            data = step_recognise_cycles(case, data, quantity=quantity, shift=ext)
            LPsub.next()
            if case.process.cycles.remove_bad:
                data = step_removed_marked_sections(case, data)
            LPsub.next()

            LPsub = LP.subtask(f'''FIT CURVE {quantity}''', 1)
            data, fits = step_fit_curve(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''CLASSIFY POINTS {quantity}''', 1)
            _, points0 = step_recognise_points(case, data, fits, quantity=quantity)
            LPsub.next()

            datas[quantity] = data
            fitinfos[quantity] = fits
            points[quantity] = points0
            LP.next()

        # align before plotting
        LPsub = LP.subtask(f'''ALIGN CYCLES''', 1)
        fits_p, fits_v = step_align_cycles(
            case,
            fitinfos_p=fitinfos['pressure'],
            points_p=points['pressure'],
            fitinfos_v=fitinfos['volume'],
            points_v=points['volume'],
        )
        fitinfos['pressure'] = fits_p
        fitinfos['volume'] = fits_v
        LPsub.next()

        # process quantities separately
        for quantity, symb in [
            ('pressure', 'P'),
            ('volume', 'V'),
        ]:
            data = datas[quantity]
            fits = fitinfos[quantity]
            points0 = points[quantity]

            LPsub = LP.subtask(f'''OUTPUT TABLES {quantity}''', 1)
            step_output_single_table(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask('''OUTPUT TIME PLOTS''', 1)
            plt = step_output_time_plot(case, data, fits, points0, quantity=quantity, symb=symb)
            # plt.show()
            LPsub.next()
            LP.next()

        # combined output
        LPsub = LP.subtask(f'''OUTPLOT P/V-LOOP PLOT''', 0)
        log_warn('Not yet implemented!')
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
