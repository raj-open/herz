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
    fitinfos: list[tuple[tuple[int, int], FittedInfo]],
    quantity: str,
) -> tuple[dict[str, list[int]], dict[str, list[float]],]:
    match quantity:
        case 'pressure':
            infos = [
                ((i1, i2), info, recognise_special_points_pressure(info))
                for (i1, i2), info in fitinfos
            ]
        case 'volume':
            infos = [
                ((i1, i2), info, recognise_special_points_volume(info))
                for (i1, i2), info in fitinfos
            ]
        case _:
            raise ValueError(f'No methods developed for quantity {quantity}!')

    # NOTE: use boolean-tags to mark whether a set of classified points has been adjusted
    keys = flatten(*[obj.keys() for _, _, obj in infos])
    calculations = [(False, {key: ([], ts) for key, ts in obj.items()}) for _, _, obj in infos]

    # adjust classified points in each cycle
    t = data['time'].to_numpy(copy=True)
    for k, ((i1, i2), info, points) in enumerate(infos[:-1]):
        # undo normalisation of time points:
        T = info.normalisation.period
        points = {key: [t[i1] + T * tt for tt in ts] for key, ts in points.items()}
        # add in tag=True + indices of time points
        calculations[k] = (
            True,
            {key: (closest_indices(ts, t[i1:i2], init=i1), []) for key, ts in points.items()},
        )

    calculations_false = [data for tag, data in calculations if not tag] + [{}]
    calculations_true = [data for tag, data in calculations if tag]

    points_normalised = {key: ts for key, (i, ts) in calculations_false[0].items()}
    points = {
        key: flatten(
            *[
                indices
                for times in calculations_true
                for key_, (indices, ts) in times.items()
                if key_ == key
            ]
        )
        for key in keys
    }

    return points, points_normalised
