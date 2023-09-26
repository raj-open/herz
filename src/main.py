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
    log_progress('''SETUP''', 0, 1)
    config.set_user_config(path)

    for case in config.CASES:
        datas = dict()
        points = dict()
        coeffs = dict()
        log_progress(f'''RUN CASE {case.label}''', -1, 5)

        for quantity, symb, cfg_data, ext in [
            ('pressure', 'P', case.data.pressure, 'peak'),
            ('volume', 'V', case.data.volume, 'trough'),
        ]:
            log_progress(f'''READ DATA {quantity}''', 0, 6)
            data = step_read_data(cfg_data, quantity)
            data = step_normalise_data(case, data, quantity=quantity)

            log_progress(f'''RECOGNISE CYCLES {quantity}''', 1, 6)
            data = step_recognise_cycles(case, data, quantity=quantity, shift=ext)
            if case.process.cycles.remove_bad:
                data = step_removed_marked_sections(case, data)

            log_progress(f'''FIT CURVE {quantity}''', 2, 6)
            data, infos = step_fit_curve(case, data, quantity=quantity)

            log_progress(f'''CLASSIFY POINTS {quantity}''', 3, 6)
            points_cycles, points_normalised = step_recognise_points(
                case, data, infos, quantity=quantity
            )

            log_progress(f'''OUTPUT TABLES {quantity}''', 4, 6)
            step_output_single_table(case, data, quantity=quantity)

            log_progress('''OUTPUT TIME PLOTS''', 5, 6)
            plt = step_output_time_plot(case, data, points_cycles, quantity=quantity, symb=symb)
            # plt.show()

            coeff = infos[-1].coefficients
            T, c, m, s = get_normalisation_params(infos[-1])
            coeff_rescaled = get_rescaled_polynomial(infos[-1])
            points_unnormalised = {key: T * tt for key, tt in points_normalised.items()}

            datas[quantity] = data
            coeffs[quantity] = coeff_rescaled
            points[quantity] = points_unnormalised
            log_info(
                dedent(
                    f'''
                Recognised period for {quantity}: T ≈ {1000 * T:.1f}ms.

                Cycles for {quantity} normalised as follows:

                1. shifted to ({ext}-{ext})
                2. time-normalised from [0, T] ---> [0, 1]
                3. linear drift removed (from {symb}(0) to {symb}(1))
                4. re-scaled so that L²-norm = 1

                Fitted Polynomial for normalised cycle of {quantity}:

                    {symb}₀(t) = {print_poly(coeff, var='t', unitise=True)}

                Fitted Polynomial for cycle of {quantity} (not normalised, excecpt for 1.):

                    {symb}(t) = {c} + {m}·t/T + {s}·{symb}₀(t/T)
                      = {print_poly(coeff_rescaled, var='t', unitise=True)}
                '''
                )
            )

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
