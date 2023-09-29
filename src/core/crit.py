#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.types import *
from ..thirdparty.render import *

from .constants import *
from ..models.enums import *
from .log import *
from .utils import *
from .constants import *
from .poly import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'get_critical_points',
    'get_critical_points_bounded',
    'clean_time_points_for_list_of_critical_points',
    'clean_time_points_for_list_of_lists_of_critical_points',
    'log_critical_points',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_critical_points(
    p: list[float],
    eps: float = FLOAT_ERR,
    dp: Optional[list[float]] = None,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[tuple[float, float, set[EnumCriticalPoints]]]:
    crit = []

    # if not precomputed, compute 1st and 2nd derivatives:
    dp = dp or get_derivative_coefficients(p)

    # necessary condition: t (real-valued) is critical ONLY IF p'(t) = 0
    t_crit = get_real_polynomial_roots(dp)

    # compute multiplicity of each root
    info = get_duplicate_times_and_multiplicity(t_crit, t_min=t_min, t_max=t_max, eps=eps)
    t_crit = [t0 for t0, _ in info]

    N = len(t_crit)
    if N == 0:
        return []

    # compute points between critical points
    C = 2 * max([abs(t0) for t0 in t_crit]) + 1
    delta = np.diff([-C] + t_crit + [C])
    t_between = [t0 - dt / 2 for (t0, dt) in zip(t_crit + [C], delta)]
    t_grid = [t_between[0]] + flatten(*list(zip(t_crit, t_between[1:])))

    # classify critical points:
    # FAST METHOD:
    N = len(t_grid)
    values = poly(t_grid, *p)
    values = [tuple(values[k - 1 :][:3]) for k in range(1, N - 1, 2)]
    for (t0, v), (ym_pre, y0, ym_post) in zip(info, values):
        # ----------------------------------------------------------------
        # NOTE:
        # Times between critical points:
        #
        #  ----O------|------O------|--------O----
        #     pre   tm_pre   t0    tm_post  post
        #
        # - y0 := p(t0)
        # - ym_pre := p(tm_pre)
        # - ym_post := p(tm_post)
        #
        # If any of these values are equal,then by mean-value-thm
        # a critical point occurs between them - contradiction!
        # Hence it is mathematically guaranteed,
        # that sgn(ym_pre - y0) = ±1
        # and sgn(ym_post - y0) = ±1
        # ----------------------------------------------------------------

        # classify based on pre/post-changes:
        change_post = sign_normalised_difference(y0, ym_post, eps=MACHINE_EPS)
        change_pre = sign_normalised_difference(ym_pre, y0, eps=MACHINE_EPS)
        match change_pre, change_post:
            case (-1, 1):
                crit.append((t0, y0, {EnumCriticalPoints.LOCAL_MINIMUM}))
            case (1, -1):
                crit.append((t0, y0, {EnumCriticalPoints.LOCAL_MAXIMUM}))
            case (-1, -1) | (1, 1):
                crit.append((t0, y0, {EnumCriticalPoints.INFLECTION}))
            case _:
                # NOTE: This case should not occur! If it does - reject!
                pass

    # compute zeroes
    t_zeroes = get_real_polynomial_roots(p)
    info = get_duplicate_times_and_multiplicity(t_zeroes, t_min=t_min, t_max=t_max, eps=eps)
    for t0 in t_zeroes:
        crit.append((t0, 0.0, {EnumCriticalPoints.ZERO}))

    # clean up classified point (e.g. combine multiply classified points)
    # NOTE: increase eps-value, to prevent duplicates
    crit = clean_time_points_for_list_of_critical_points(
        crit, t_min=t_min, t_max=t_max, eps=100 * eps
    )

    # deal with inflection points
    crit = handle_inflection_points(crit)

    return crit


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS include bounds
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_critical_points_bounded(
    p: list[float],
    eps: float = FLOAT_ERR,
    dp: Optional[list[float]] = None,
    t_min: float = 0.0,
    t_max: float = 1.0,
) -> list[tuple[float, float, set[EnumCriticalPoints]]]:
    crit = get_critical_points(p=p, dp=dp, t_min=t_min, t_max=t_max, eps=eps)

    # restrict to interval
    crit = [(t0, y0, kinds) for (t0, y0, kinds) in crit if t_min <= t0 and t0 <= t_max]

    if len(crit) == 0:
        return []

    t_crit = [crit[0][0], crit[-1][0]]
    values = poly([t_min, t_max], *p)

    # add in left-boundary or purify points that are too close
    if abs(t_crit[0] - t_min) < eps:
        crit[0] = (t_min, values[0], *crit[0][2:])
    else:
        crit.insert(0, (t_min, values[0], set()))

    # add in right-boundary or purify points that are too close
    if abs(t_max - t_crit[-1]) < eps:
        crit[-1] = (t_max, values[-1], *crit[-1][2:])
    else:
        t_crit.append(t_max)
        crit.append((t_max, values[-1], set()))

    # compute absoulte min/max
    values = [y0 for t0, y0, kind in crit]
    y_min = np.min(values)
    y_max = np.max(values)
    for k, (t0, y0, kinds) in enumerate(crit):
        if abs(normalised_difference(y_max, y0)) < MACHINE_EPS:
            crit[k] = (
                t0,
                y_max,
                kinds.union({EnumCriticalPoints.MAXIMUM}),
            )
        elif abs(normalised_difference(y_min, y0)) < MACHINE_EPS:
            crit[k] = (
                t0,
                y_min,
                kinds.union({EnumCriticalPoints.MINIMUM}),
            )

    # remove points with no classification
    crit = [(t0, y0, kinds) for t0, y0, kinds in crit if len(kinds) > 0]

    return crit


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - multiple series of critical points
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def clean_time_points_for_list_of_critical_points(
    crit: list[tuple[float, float, set[EnumCriticalPoints]]],
    eps: float = FLOAT_ERR,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[list[tuple[float, float, set[EnumCriticalPoints]]]]:
    if len(crit) == 0:
        return []

    # find unique time-values
    times = get_times_from_list_of_critical_points(crit, t_min=t_min, t_max=t_max)
    t_min = min(times)
    t_max = max(times)

    # remove ε-duplicates
    times = get_duplicate_times([t_min] + times + [t_max], t_min=t_min, t_max=t_max, eps=eps)

    # forcibly ensure the boundary-values
    times[0] = t_min
    times[-1] = t_max

    # gather ε-duplicates
    crit_duplicates = [
        (t0, [(y0, kinds) for t0_, y0, kinds in crit if closest_index(t0_, times) == i])
        for i, t0 in enumerate(times)
    ]

    # combine ε-duplicates
    crit = [
        (t0, obj[0][0], set().union(*[kinds for y0, kinds in obj]))
        for t0, obj in crit_duplicates
        if len(obj) > 0
    ]

    return crit


def clean_time_points_for_list_of_lists_of_critical_points(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    eps: float = FLOAT_ERR,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[list[tuple[float, float, set[EnumCriticalPoints]]]]:
    if len(crits) == 0:
        return []

    # find unique time-values
    times = get_times_from_list_of_lists_of_critical_points(crits, t_min=t_min, t_max=t_max)
    t_min = min(times)
    t_max = max(times)

    # remove ε-duplicates
    times = get_duplicate_times([t_min] + times + [t_max], eps=eps)

    # forcibly ensure the boundary-values
    times[0] = t_min
    times[-1] = t_max

    # rewrite time-values
    crits = [
        [(closest_value(t0, times), y0, kinds) for t0, y0, kinds in crit] for crit in crits
    ]

    return crits


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - representations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def log_critical_points(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> str:
    n_der = len(crits) - 1
    classifications = gather_multi_level_critical_points_classifications(
        crits, t_min=t_min, t_max=t_max
    )
    data = []
    for t0, classif in classifications:
        class_as_strs = [
            ', '.join([kind.value for kind in kinds]) if len(kinds) > 0 else None
            for kinds in classif
        ]
        data.append([f'{t0:.6f}'] + class_as_strs)
    table = tabulate(
        data,
        headers=['t'] + [f'crit p{"´" * n}' for n in range(n_der + 1)],
        tablefmt='pretty',
        floatfmt='.4f',
        stralign='left',
        missingval='—',
        showindex=False,
        colalign=['right'] + ['center'] * (n_der + 1),
        rowalign='top',
    )
    return table


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def handle_inflection_points(
    crit: list[tuple[float, float, set[EnumCriticalPoints]]]
) -> list[tuple[float, float, set[EnumCriticalPoints]]]:
    minmax = {EnumCriticalPoints.LOCAL_MINIMUM, EnumCriticalPoints.LOCAL_MAXIMUM}
    for k, (t0, y0, kinds) in enumerate(crit):
        if minmax.issubset(kinds):
            kinds = kinds.difference(minmax).union({EnumCriticalPoints.INFLECTION})
            crit[k] = (t0, y0, kinds)
    return crit


def get_duplicate_times(
    t: list[float],
    eps: float,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[tuple[float, int]]:
    '''
    Determines if certain points occur "too closely" together,
    and views these as duplicates.
    '''
    info = get_duplicate_times_and_multiplicity(t, t_min=t_min, t_max=t_max, eps=eps)
    return [t0 for t0, _ in info]


def get_duplicate_times_and_multiplicity(
    t: list[float],
    eps: float,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[tuple[float, int]]:
    '''
    Determines if certain points occur "too closely" together,
    and views these as duplicates.
    '''
    if len(t) == 0:
        return []
    t = sorted(t)
    C = 2 * max([abs(tt) for tt in t] + [0]) + 1
    delta = np.diff([-C] + t + [C])  # difference between each point and previous neighbour
    indices = characteristic_to_where(delta >= eps)
    info = []
    for k1, k2 in zip(indices, indices[1:]):
        info.append((t[k1], k2 - k1))

    if abs(t_min) < np.inf:
        i = closest_index(t_min, [tt for tt, v in info])
        tt, v = info[i]
        if abs(t_min - tt) < eps:
            info[i] = (t_min, v)

    if abs(t_max) < np.inf:
        i = closest_index(t_max, [tt for tt, v in info])
        tt, v = info[i]
        if abs(t_max - tt) < eps:
            info[i] = (t_min, v)

    info = [(tt, v) for tt, v in info if t_min <= tt and tt <= t_max]
    return info


def get_times_from_list_of_critical_points(
    crit: list[tuple[float, float, set[EnumCriticalPoints]]],
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[float]:
    times = [t0 for t0, y0, kinds in crit if len(kinds) > 0 and t_min < t0 and t0 < t_max]
    if abs(t_min) < np.inf:
        times.insert(0, t_min)
    if abs(t_max) < np.inf:
        times.append(t_max)
    times = unique(sorted(times))
    return times


def get_times_from_list_of_lists_of_critical_points(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[float]:
    times = get_times_from_list_of_critical_points(flatten(*crits))
    return times


def gather_multi_level_critical_points_classifications(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[tuple[float, list[dict[EnumCriticalPoints]]]]:
    crits = clean_time_points_for_list_of_lists_of_critical_points(
        crits, t_min=t_min, t_max=t_max
    )
    times = get_times_from_list_of_lists_of_critical_points(crits, t_min=t_min, t_max=t_max)

    if abs(t_min) < np.inf and t_min not in times:
        times.insert(0, t_min)
    if abs(t_max) < np.inf and t_max not in times:
        times.append(t_max)

    classifications = [
        (
            t0,
            [set().union(*[kinds for t0_, y0, kinds in crit if t0_ == t0]) for crit in crits],
        )
        for t0 in times
    ]
    return classifications
