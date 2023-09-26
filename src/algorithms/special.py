#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *

from ..core.log import *
from ..core.constants import *
from ..core.poly import *
from ..models.internal import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'recognise_special_points_pressure',
    'recognise_special_points_volume',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def recognise_special_points_pressure(info: FittedInfo) -> dict[str, float]:
    # NOTE: see documentation/README.md for definitions.
    n_der = 2

    # Get polynomial coefficients of n-th derivatives of curve.
    # NOTE: dx[k] = coeff's of k-th derivative of polynomial x(t)
    dx: list[list[float]] = [[]] * (n_der + 2)
    dx[0] = info.coefficients
    for k in range(n_der + 1):
        dx[k + 1] = get_derivative_coefficients(dx[k])
    # compute and classify critical points of derivatives:
    crits = [
        get_critical_points_bounded(
            p=dx[k],
            dp=dx[k + 1],
            t_min=0.0,
            t_max=1.0,
            only_min_max=True,
        )
        for k in range(n_der + 1)
    ]
    crits_localmin, crits_min, crits_localmax, crits_max = split_critical_points(crits)

    # RECOGNISE esp:

    # RECOGNISE anti_epad:

    # RECOGNISE sdp:

    # RECOGNISE dia:

    # RECOGNISE edp:

    # RECOGNISE epad:

    # RECOGNISE eivc:

    # RECOGNISE sys:

    return {}


def recognise_special_points_volume(info: FittedInfo) -> dict[str, float]:
    # NOTE: see documentation/README.md for definitions.
    # TODO: implement this
    log_warn('Classification of volume points not yet implemented!')
    return {}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def split_critical_points(
    crits: list[list[tuple[float, int, CriticalPoint]]],
) -> tuple[
    list[list[tuple[float, int, CriticalPoint]]],
    list[list[tuple[float, int, CriticalPoint]]],
    list[list[tuple[float, int, CriticalPoint]]],
    list[list[tuple[float, int, CriticalPoint]]],
]:
    crits_localmin = [
        [
            (t0, y0, v, kind)
            for t0, y0, v, kind in crit
            if kind in [CriticalPoint.LOCAL_MINIMUM, CriticalPoint.MINIMUM]
        ]
        for crit in crits
    ]

    crits_min = [
        [(t0, y0, v, kind) for t0, y0, v, kind in crit if kind == CriticalPoint.MINIMUM]
        for crit in crits
    ]

    crits_localmax = [
        [
            (t0, y0, v, kind)
            for t0, y0, v, kind in crit
            if kind in [CriticalPoint.LOCAL_MAXIMUM, CriticalPoint.MAXIMUM]
        ]
        for crit in crits
    ]

    crits_max = [
        [(t0, y0, v, kind) for t0, y0, v, kind in crit if kind == CriticalPoint.MAXIMUM]
        for crit in crits
    ]

    return crits_localmin, crits_min, crits_localmax, crits_max


def filter_times(
    crit: list[tuple[float, int, CriticalPoint]],
    t_after: float = -np.inf,
    t_before: float = np.inf,
):
    return [(t0, y0, v, kind) for t0, y0, v, kind in crit if t_after < t0 and t0 < t_before]
