#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.data import *
from ..thirdparty.maths import *

from ..setup import config
from ..algorithms.cycles import *
from ..algorithms.special import *
from ..models.user import *
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'step_recognise_special_points',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def step_recognise_special_points(
    case: UserCase,
    data: pd.DataFrame,
    infos: list[FittedInfo],
    quantity: str,
) -> list[tuple[bool, dict[str, tuple[int, float]]]]:
    match quantity:
        case 'pressure':
            classified0 = [recognise_special_points_pressure(info) for info in infos]
        case 'volume':
            classified0 = [recognise_special_points_volume(info) for info in infos]
        case _:
            raise ValueError(f'No methods developed for quantity {quantity}!')

    # NOTE: use boolean-tags to mark whether a set of classified points has been adjusted
    classified = [(False, {key: (-1, tt) for key, tt in obj.items()}) for obj in classified0]

    # adjust classified points in each cycle
    t = data['time'].to_numpy(copy=True)
    cycles = data['cycle'].tolist()
    windows = cycles_to_windows(cycles)
    for k, ((i1, i2), points) in enumerate(zip(windows, classified0)):
        # undo normalisation of time points:
        T = infos[k].normalisation.period
        points = {key: t[i1] + T * tt for key, tt in points.items()}
        # add in tag=True + indices of time points
        classified[k] = (
            True,
            {key: (closest_index(tt, t[i1:i2], init=i1), tt) for key, tt in points.items()},
        )

    return classified
