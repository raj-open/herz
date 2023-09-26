#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
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
    infos: list[FittedInfo],
    quantity: str,
) -> tuple[dict[str, list[int]], dict[str, float],]:
    match quantity:
        case 'pressure':
            times = [recognise_special_points_pressure(info) for info in infos]
        case 'volume':
            times = [recognise_special_points_volume(info) for info in infos]
        case _:
            raise ValueError(f'No methods developed for quantity {quantity}!')

    # NOTE: use boolean-tags to mark whether a set of classified points has been adjusted
    keys = flatten(*[obj.keys() for obj in times])
    calculations = [(False, {key: (-1, tt) for key, tt in obj.items()}) for obj in times]

    # adjust classified points in each cycle
    t = data['time'].to_numpy(copy=True)
    cycles = data['cycle'].tolist()
    windows = cycles_to_windows(cycles)
    for k, ((i1, i2), points) in enumerate(zip(windows, times)):
        # undo normalisation of time points:
        T = infos[k].normalisation.period
        points = {key: t[i1] + T * tt for key, tt in points.items()}
        # add in tag=True + indices of time points
        calculations[k] = (
            True,
            {key: (closest_index(tt, t[i1:i2], init=i1), tt) for key, tt in points.items()},
        )

    calculations_false = [times for tag, times in calculations if not tag] + [{}]
    calculations_true = [times for tag, times in calculations if tag]

    points_normalised = {key: tt for key, (i, tt) in calculations_false[0].items()}
    points = {
        key: [
            i for times in calculations_true for key_, (i, tt) in times.items() if key_ == key
        ]
        for key in keys
    }

    return points, points_normalised
