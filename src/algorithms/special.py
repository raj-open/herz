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


def recognise_special_points_pressure(info: FittedInfo) -> dict[str, list[float]]:
    times = {}

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
        get_critical_points_bounded(p=dx[k], dp=dx[k + 1], t_min=0.0, t_max=1.0)
        for k in range(n_der + 1)
    ]
    crits_localmin = filter_kinds(crits, [CriticalPoint.LOCAL_MINIMUM, CriticalPoint.MINIMUM])
    crits_min = filter_kinds(crits, [CriticalPoint.MINIMUM])
    crits_localmax = filter_kinds(crits, [CriticalPoint.LOCAL_MAXIMUM, CriticalPoint.MAXIMUM])
    crits_max = filter_kinds(crits, [CriticalPoint.MAXIMUM])

    # RECOGNISE sys:
    # times['sys'] = [0.0, 1.0]
    times['sys'] = [0.0]
    t0 = 0.0

    # RECOGNISE dia:
    crit = filter_times(crits_localmin[0], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['dia'] = [t0]

    # RECOGNISE edp:
    crit = filter_times(crits_localmax[2], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['edp'] = [t0]

    # RECOGNISE epad:
    crit = filter_times(crits_localmax[1], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['epad'] = [t0]

    # RECOGNISE eivc:
    crit = filter_times(crits_localmin[2], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['eivc'] = [t0]

    # MODULO PEAK:
    t0 = 0

    # RECOGNISE esp:
    crit = filter_times(crits_localmin[2], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['esp'] = [t0]

    # RECOGNISE anti_epad:
    crit = filter_times(crits_localmin[1], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['anti-epad'] = [t0]

    # RECOGNISE sdp:
    crit = filter_times(crits_localmax[2], t_after=t0, t_before=1.0)
    t0 = crit[0][0]
    times['sdp'] = [t0]

    # RECOGNISE start-end of cycle (for plotting):
    t_split = (times['edp'][0] + times['epad'][0]) / 2
    times['split'] = [t_split]

    return times


def recognise_special_points_volume(info: FittedInfo) -> dict[str, list[float]]:
    # NOTE: see documentation/README.md for definitions.
    # TODO: implement this
    log_warn('Classification of volume points not yet implemented!')
    return {}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def filter_kinds(
    crits: list[list[tuple[float, int, CriticalPoint]]], kinds: list[CriticalPoint]
) -> list[list[tuple[float, int, CriticalPoint]]]:
    return [[(t0, y0, v, kind) for t0, y0, v, kind in crit if kind in kinds] for crit in crits]


def filter_times(
    crit: list[tuple[float, int, CriticalPoint]],
    t_after: float = -np.inf,
    t_before: float = np.inf,
):
    return [(t0, y0, v, kind) for t0, y0, v, kind in crit if t_after < t0 and t0 < t_before]
