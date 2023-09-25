#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from .core.log import *
from .setup import config
from src.steps import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def enter(path: str, *_):
    log_progress('''SETUP''', 0, 1)
    config.set_user_config(path)

    for case in config.CASES:
        datas = dict()
        coeffs = dict()
        Ts = dict()
        log_progress(f'''RUN CASE {case.label}''', -1, 5)

        for quantity, symb, cfg_data, ext in [
            ('pressure', 'P', case.data.pressure, 'peak'),
            ('volume', 'V', case.data.volume, 'trough'),
        ]:
            log_progress(f'''READ DATA {quantity}''', 0, 5)
            data = step_read_data(cfg_data, quantity)
            data = step_normalise_data(case, data, quantity=quantity)

            log_progress(f'''PROCESS DATA {quantity}''', 1, 5)
            data, T = step_recognise_cycles(case, data, quantity=quantity, shift=ext)
            if case.process.cycles.remove_bad:
                data = step_removed_marked_sections(case, data)
            data, coeff = step_fit_curve(case, data, quantity=quantity)
            log_info(f'Recognised period for {quantity}: {1000 * T:.1f}ms.')

            log_progress(f'''OUTPUT TABLES {quantity}''', 2, 5)
            step_output_single_table(case, data, quantity=quantity)

            log_progress('''OUTPUT TIME PLOTS''', 3, 5)
            plt = step_output_time_plot(case, data, quantity=quantity, symb=symb)
            # plt.show()

            datas[quantity] = data
            Ts[quantity] = T
            coeffs[quantity] = coeff

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
