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
    'step_recognise_points',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@echo_function(message='STEP recognise special points', level=LOG_LEVELS.INFO)
def step_recognise_points(
    data: pd.DataFrame,
    fits: list[tuple[tuple[int, int], FittedInfoPoly]],
    cfg: dict[str, SpecialPointsConfig],
    key_align: str,
) -> tuple[dict[str, SpecialPointsConfig], list[tuple[tuple[int, int], dict[str, int]]]]:
    '''
    Uses fitted model to automatically recognise points based on derivative-conditions.
    '''
    search = sort_special_points_specs(cfg)
    N = len(fits)
    window_info_points = [
        recognise_special_points(info, search=search, skip_errors=i < N - 1) for i, (_, info) in enumerate(fits)
    ]

    # adjust classified points in each cycle:
    t = data['time'].to_numpy(copy=True)
    points_data = [
        (
            (i1, i2),
            {key: closest_index(point.time, points=t[i1:i2]) for key, point in points.items()},
        )
        for ((i1, i2), _), points in zip(fits[:-1], window_info_points[:-1])
    ]

    # add in aligment point
    points_data = [(win, points | {'align': points.get(key_align, -1)}) for win, points in points_data]

    # final window contains point-information for fitted cycle:
    special = window_info_points[-1]

    # add in aligment point
    special['align'] = SpecialPointsConfig(
        name='align',
        ignore=True,
        time=special[key_align].time,
    )

    return special, points_data
