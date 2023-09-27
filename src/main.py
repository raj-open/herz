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
        points = dict()
        coeffs = dict()
        LP = LogProgress(f'''RUN CASE {case.label}''', steps=3)

        # process quantities separately
        for quantity, symb, cfg_data, ext in [
            ('pressure', 'P', case.data.pressure, 'peak'),
            ('volume', 'V', case.data.volume, 'trough'),
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
            data, fitinfos = step_fit_curve(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''CLASSIFY POINTS {quantity}''', 1)
            _, points0 = step_recognise_points(case, data, fitinfos, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask(f'''OUTPUT TABLES {quantity}''', 1)
            step_output_single_table(case, data, quantity=quantity)
            LPsub.next()

            LPsub = LP.subtask('''OUTPUT TIME PLOTS''', 1)
            plt = step_output_time_plot_ideal(
                case, data, fitinfos, points0, quantity=quantity, symb=symb
            )
            # plt.show()
            LPsub.next()
            LP.next()

        # alig
        LP.next()

        # _, info = fitinfos[-1]
        # coeff0 = info.coefficients
        # T, c, m, s = get_normalisation_params(info)
        # coeff1, points1 = get_rescaled_polynomial_and_points(info, points0)

        # datas[quantity] = data
        # coeffs[quantity] = coeff1
        # points[quantity] = points1

        # TODO - handle combined outputs
        # step_output_combined_table(case, datas, coeffs)
        # step_output_loop_plot(case, datas, coeffs)

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
