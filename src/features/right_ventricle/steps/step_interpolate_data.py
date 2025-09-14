#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------


import numpy as np
import pandas as pd

from ....algorithms.anomalies import *
from ....algorithms.interpolations import *
from ....core.log import *
from ....models.app import *
from ....models.fitting import *
from ....thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "step_interpolate_pv",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message="STEP interpolate series into P-V curve", level=LOG_LEVELS.INFO)
def step_interpolate_pv(
    data_p: pd.DataFrame,
    data_v: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combines every cycle of the volume data series
    with every cycle of the pressure data series.

    Each combination consists of comensurating series with possibly incompatible time axes,
    thus applies linear interpolation to iron out this issue.
    """
    windows_p = cycles_to_windows(data_p["cycle"])
    windows_v = cycles_to_windows(data_v["cycle"])

    PV = np.zeros(shape=(0, 4))

    for i_v, j_v in windows_v:
        t_v = data_v[i_v:j_v]["time"].to_numpy(copy=True)
        t_v, _, _, _ = normalise_to_unit_interval(t_v)
        V = data_v[i_v:j_v]["volume"].to_numpy(copy=True)

        for i_p, j_p in windows_p:
            t_p = data_p[i_p:j_p]["time"].to_numpy(copy=True)
            t_p, _, _, _ = normalise_to_unit_interval(t_p)
            P = data_p[i_p:j_p]["pressure"].to_numpy(copy=True)
            t_, dt_, V_, P_ = interpolate_two_series(t1=t_v, x1=V, t2=t_p, x2=P)
            PV_ = np.asarray([t_, dt_, V_, P_]).T
            PV = np.concatenate([PV, PV_])

    data = pd.DataFrame(
        {
            "time": PV[:, 0],
            "dt": PV[:, 1],
            "volume": PV[:, 2],
            "pressure": PV[:, 3],
        }
    )

    return data
