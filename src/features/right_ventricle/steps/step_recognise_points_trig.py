#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....algorithms.critical import *
from ....core.log import *
from ....models.app import *
from ....models.epsilon import *
from ....models.fitting import *
from ....models.polynomials import *
from ....models.user import *
from ....queries.fitting import *
from ....thirdparty.data import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_recognise_iso_from_trig",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP recognise iso from trig", level=LOG_LEVELS.INFO)
def step_recognise_iso_from_trig(
    fit: FittedInfoTrig,
    special: dict[str, SpecialPointsConfig],
) -> dict[str, SpecialPointsConfig]:
    point = special["iso"]
    t0 = fit.hshift
    point.time = t0
    point.value = fit.vshift + fit.drift * t0 + fit.vscale
    point.found = True
    return special
