#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.misc import *
from ....thirdparty.types import *

from ....core.log import *
from ....core.constants import *
from ....models.app import *
from ....models.enums import *
from ....models.fitting import *
from ....models.polynomials import *
from ....queries.fitting import *

# from ....algorithms.fitting.exponential import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_fit_exp_pressure',
    'step_fit_exp_volume',
    'step_fit_exp_pv',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP fit exp-model to P-V curve', level=LOG_LEVELS.INFO)
def step_fit_exp_pv():
    log_warn('Combine to P-V model - not implemented')
    return


@echo_function(message='STEP fit lineare-model to P-curve', level=LOG_LEVELS.INFO)
def step_fit_exp_pressure():
    log_warn('Fit line to P - not implemented')
    return


@echo_function(message='STEP fit logarithmic-model to V-curve', level=LOG_LEVELS.INFO)
def step_fit_exp_volume():
    log_warn('Fit log to V - not implemented')
    return
