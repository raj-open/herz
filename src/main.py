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
        log_progress('''READ DATA''', 0, 2)
        data_pressure, data_volume = step_read_data(case)
        data = step_combine_data(case, data_pressure, data_volume)

        log_progress('''PROCESS DATA''', 0, 4)
        data = step_compute_extremes(case, data, quantities=['pressure', 'volume'])
        data = step_recognise_cycles(case, data, quantity='pressure')
        if case.process.cycles.remove_bad:
            data = step_removed_marked_sections(case, data)
        data = step_fit_curve(case, data, quantities=['pressure', 'volume'])

        log_progress('''OUTPUT TABLES''', 0, 1)
        step_output_tables(case, data)

        log_progress('''OUTPUT TIME PLOTS''', 0, 1)
        plt_p, plt_v = step_output_time_plots(case, data)
        # plt_p.show()
        # plt_v.show()

        log_progress('''OUTPUT LOOP PLOTS''', 0, 1)
        plt = step_output_loop_plot(data)
        # plt.show()
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SECONDARY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXCEUTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    args = sys.argv[1:]
    enter(*args)
