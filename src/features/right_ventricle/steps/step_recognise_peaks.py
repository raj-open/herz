#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....algorithms.anomalies import *
from ....core.log import *
from ....core.utils import *
from ....models.app import *
from ....models.user import *
from ....thirdparty.data import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_recognise_peaks",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP recognise peaks", level=LOG_LEVELS.INFO)
def step_recognise_peaks(
    data: pd.DataFrame,
    quantity: str,
) -> pd.DataFrame:
    N = len(data)
    values = data[quantity]
    peaks, troughs = get_extremes(values)
    data[f"{quantity}[peak]"] = where_to_characteristic(peaks, N)
    data[f"{quantity}[trough]"] = where_to_characteristic(troughs, N)
    return data
