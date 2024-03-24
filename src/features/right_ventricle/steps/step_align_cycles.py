#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....core.log import *
from ....models.user import *
from ....models.fitting import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_align_cycles',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP align cycles', level=LOG_LEVELS.INFO)
def step_align_cycles(
    case: RequestConfig,
    fitinfos_p: list[tuple[tuple[int, int], FittedInfo]],
    fitinfos_v: list[tuple[tuple[int, int], FittedInfo]],
    points_p: dict[str, list[float]],
    points_v: dict[str, list[float]],
) -> tuple[
    list[tuple[tuple[int, int], FittedInfo]],
    list[tuple[tuple[int, int], FittedInfo]],
]:
    '''
    Adjusts volume data, so that it aligns with pressure data.
    '''
    _, infos_p = fitinfos_p[-1]
    _, infos_v = fitinfos_v[-1]
    T_p = infos_p.normalisation.period
    T_v = infos_v.normalisation.period
    scale = T_p / T_v
    log_warn('Not yet implemented')
    return fitinfos_p, fitinfos_v
