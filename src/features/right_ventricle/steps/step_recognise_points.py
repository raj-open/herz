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
from ....queries.fitting import *
from ....algorithms.critical import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_recognise_points',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP recognise special points', level=LOG_LEVELS.INFO)
def step_recognise_points(
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    special: dict[str, SpecialPointsConfig],
) -> tuple[dict[str, SpecialPointsConfig], list[tuple[tuple[int, int], dict[str, int]]]]:
    '''
    Uses fitted model to automatically recognise points based on derivative-conditions.
    '''
    special_ = sort_special_points_specs(special)
    N = len(fitinfos[:-1])
    window_info_points = [recognise_special_points(info, special=special_) for _, info in fitinfos]

    # final window contains point-information for fitted cycle:
    points_fit = window_info_points[-1]

    # adjust classified points in each cycle:
    t = data['time'].to_numpy(copy=True)
    points_data = [
        (
            (i1, i2),
            {
                key: closest_index(t[i1] + info.normalisation.period * point.time, t[i1:i2])
                for key, point in points.items()
            },
        )
        for ((i1, i2), info), points in zip(fitinfos[:-1], window_info_points[:-1])
    ]

    return points_fit, points_data
