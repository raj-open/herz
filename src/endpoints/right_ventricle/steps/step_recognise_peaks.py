#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *

from ....core.utils import *
from ....models.app import *
from ....models.user import *
from ....algorithms.peaks import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_recognise_peaks',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def step_recognise_peaks(
    case: RequestConfig,
    cfg: AppConfig,
    data: pd.DataFrame,
    quantity: str,
) -> pd.DataFrame:
    N = len(data)
    values = data[quantity]
    peaks, troughs = get_extremes(values)
    data[f'{quantity}[peak]'] = where_to_characteristic(peaks, N)
    data[f'{quantity}[trough]'] = where_to_characteristic(troughs, N)
    return data
