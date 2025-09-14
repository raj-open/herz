#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np
import pandas as pd

from ....algorithms.anomalies import *
from ....core.utils import *
from ....models.user import *
from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "recocompute_time_axis",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def recocompute_time_axis(
    data: pd.DataFrame,
    dt: float,
) -> pd.DataFrame:
    N = len(data)
    T_max = N * dt
    data["time[orig]"] = data["time"]
    data["time"] = np.linspace(start=0.0, stop=T_max, num=N, endpoint=False)
    return data
