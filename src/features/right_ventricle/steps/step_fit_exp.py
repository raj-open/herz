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
from ....algorithms.fitting.exponential import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_fit_exp',
    'step_fit_exp_pressure',
    'step_fit_exp_volume',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP fit exp-model to P-V curve', level=LOG_LEVELS.INFO)
def step_fit_exp(
    data_p: pd.DataFrame,
    data_v: pd.DataFrame,
    info_p: FittedInfo,
    info_v: FittedInfo,
    special_p: dict[str, SpecialPointsConfig],
    special_v: dict[str, SpecialPointsConfig],
    cfg_fit: FitExpConfig,
):
    log_warn('Combine to P-V model - not implemented')

    conf_ = cfg_fit.points
    env = {
        f'P': special_p,
        f'V': special_v,
        f'T_p': info_p.normalisation.period,
        f'T_v': info_v.normalisation.period,
    }
    env = get_schema_from_settings(conf_, env=env)

    # TODO
    log_warn('Not yet implemented!')

    return


@echo_function(message='STEP fit lineare-model to P-curve', level=LOG_LEVELS.INFO)
def step_fit_exp_pressure(
    #
):
    log_warn('Not yet implemented!')
    return


@echo_function(message='STEP fit logarithmic-model to V-curve', level=LOG_LEVELS.INFO)
def step_fit_exp_volume(
    #
):
    log_warn('Not yet implemented!')
    return
