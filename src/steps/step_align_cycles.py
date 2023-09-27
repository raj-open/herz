#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.physics import *

from ..setup import config
from ..models.user import *
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_align_cycles',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_align_cycles(
    case: UserCase,
    fitinfos_p: list[tuple[tuple[int, int], FittedInfo]],
    fitinfos_v: list[tuple[tuple[int, int], FittedInfo]],
    points_p: dict[str, list[float]],
    points_v: dict[str, list[float]],
) -> tuple[list[tuple[tuple[int, int], FittedInfo]], list[tuple[tuple[int, int], FittedInfo]],]:
    '''
    Adjusts volume data, so that it aligns with pressure data.
    '''
    _, infos_p = fitinfos_p[-1]
    _, infos_v = fitinfos_v[-1]
    T_p = infos_p.normalisation.period
    T_v = infos_v.normalisation.period
    scale = T_p / T_v
    return fitinfos_p, fitinfos_v
