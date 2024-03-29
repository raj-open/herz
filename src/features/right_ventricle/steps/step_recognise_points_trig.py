#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *

from ....core.log import *
from ....models.app import *
from ....models.user import *
from ....models.epsilon import *
from ....models.fitting import *
from ....models.polynomials import *
from ....queries.fitting import *
from ....algorithms.critical import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_recognise_iso',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP recognise iso', level=LOG_LEVELS.INFO)
def step_recognise_iso(
    fit: FittedInfoTrig,
    special: dict[str, SpecialPointsConfig],
) -> dict[str, SpecialPointsConfig]:
    point = special['iso']
    t0 = fit.hshift
    point.time = t0
    point.value = fit.vshift + fit.drift * t0 + fit.vscale
    point.found = True
    return special
