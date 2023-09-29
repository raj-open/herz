#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..setup.series import *
from ..core.utils import *
from ..algorithms.cycles import *
from ..algorithms.special import *
from ..models.user import *
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_recognise_points',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_recognise_points(
    case: UserCase,
    data: pd.DataFrame,
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
) -> tuple[list[tuple[tuple[int, int], dict[str, int]]], dict[str, SpecialPointsConfig]]:
    '''
    Uses fitted model to automatically recognise points based on derivative-conditions.
    '''
    points_unsorted = get_point_settings(quantity)
    points_sorted = sort_special_points_specs(points_unsorted)

    match quantity:
        case 'pressure':
            window_info_points = [
                ((i1, i2), info, recognise_special_points(info, points=points_sorted))
                for (i1, i2), info in fitinfos
            ]
        case 'volume':
            window_info_points = [
                ((i1, i2), info, recognise_special_points(info, points=points_sorted))
                for (i1, i2), info in fitinfos
            ]
        case _:
            raise ValueError(f'No methods developed for quantity {quantity}!')

    # final window contains point-information for fitted cycle:
    _, _, points_fit = window_info_points[-1]

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
        for (i1, i2), info, points in window_info_points[:-1]
    ]

    return points_data, points_fit
