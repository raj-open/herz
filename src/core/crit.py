#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.maths import *
from ..thirdparty.types import *
from ..thirdparty.render import *

from .constants import *
from ..models.enums import *
from .log import *
from .utils import *
from .epsilon import *
from .poly import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_critical_points',
    'get_critical_points_bounded',
    'clean_up_critical_points',
    'log_critical_points',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


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

    # remove eps-close points
    t_crit, _ = duplicates_get_assignment_maps(t_crit, eps=eps, real_valued=True)
    N = len(t_crit)
    if N == 0:
        return []

    # compute points between critical points
    t_grid = get_time_grid(t_crit, t_min=t_min, t_max=t_max, eps=eps)

    # classify critical points:
    # FAST METHOD:
    N = len(t_grid)
    values = poly(t_grid, *p)
    for k in range(1, N - 1, 2):
        t0 = t_grid[k]
        ym_pre, y0, ym_post = values[k - 1 :][:3]
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
        change_pre = sign_normalised_difference(x_from=ym_pre, x_to=y0, eps=MACHINE_EPS)
        change_post = sign_normalised_difference(x_from=y0, x_to=ym_post, eps=MACHINE_EPS)
        match change_pre, change_post:
            case (EnumSign.REAL_NEGATIVE, EnumSign.REAL_POSITIVE):
                crit.append((t0, y0, {EnumCriticalPoints.LOCAL_MINIMUM}))
            case (EnumSign.REAL_POSITIVE, EnumSign.REAL_NEGATIVE):
                crit.append((t0, y0, {EnumCriticalPoints.LOCAL_MAXIMUM}))
            case (EnumSign.REAL_NEGATIVE, EnumSign.REAL_NEGATIVE) | (
                EnumSign.REAL_POSITIVE,
                EnumSign.REAL_POSITIVE,
            ):
                crit.append((t0, y0, {EnumCriticalPoints.INFLECTION}))
            case _:
                # NOTE: This case should not occur! If it does - reject!
                pass

    # add in zeroes
    # NOTE: increase eps-value, to prevent duplicates
    t_zeroes = get_real_polynomial_roots(p)
    t_zeroes, _ = duplicates_get_assignment_maps(t_zeroes, eps=eps, boundaries_real=(t_min, t_max), real_valued=True)  # fmt: skip
    times = [t0 for t0, y0, kinds in crit]
    for t0 in t_zeroes:
        if len(times) > 0:
            i = closest_index(t0, times)
            t0_, _, kinds = crit[i]
            if is_epsilon_eq(t0_, t0, eps=100 * eps):
                crit[i] = (t0, 0.0, kinds.union({EnumCriticalPoints.ZERO}))
                continue
        crit.append((t0, 0.0, {EnumCriticalPoints.ZERO}))

    # deal with inflection points
    crit = handle_inflection_points(crit)

    # sort points
    crit = sorted(crit, key=lambda obj: obj[0])

    return crit


# ----------------------------------------------------------------
# METHODS include bounds
# ----------------------------------------------------------------


def get_critical_points_bounded(
    p: list[float],
    eps: float = FLOAT_ERR,
    dp: Optional[list[float]] = None,
    t_min: float = 0.0,
    t_max: float = 1.0,
) -> list[tuple[float, float, set[EnumCriticalPoints]]]:
    crit = get_critical_points(p=p, dp=dp, t_min=t_min, t_max=t_max, eps=eps)

    if len(crit) == 0:
        return []

    t_crit = [crit[0][0], crit[-1][0]]
    values = poly([t_min, t_max], *p)

    # add in left-boundary or purify points that are too close
    if is_epsilon_eq(t_min, t_crit[0], eps=eps):
        crit[0] = (t_min, values[0], *crit[0][2:])
    else:
        crit.insert(0, (t_min, values[0], set()))

    # add in right-boundary or purify points that are too close
    if is_epsilon_eq(t_max, t_crit[-1], eps=eps):
        crit[-1] = (t_max, values[-1], *crit[-1][2:])
    else:
        t_crit.append(t_max)
        crit.append((t_max, values[-1], set()))

    # compute absoulte min/max
    values = [y0 for t0, y0, kind in crit]
    y_min = np.min(values)
    y_max = np.max(values)
    for k, (t0, y0, kinds) in enumerate(crit):
        if is_epsilon_eq(y_max, y0, eps=MACHINE_EPS):
            crit[k] = (
                t0,
                y_max,
                kinds.union({EnumCriticalPoints.MAXIMUM}),
            )
        elif is_epsilon_eq(y_min, y0, eps=MACHINE_EPS):
            crit[k] = (
                t0,
                y_min,
                kinds.union({EnumCriticalPoints.MINIMUM}),
            )

    # remove points with no classification
    crit = [(t0, y0, kinds) for t0, y0, kinds in crit if len(kinds) > 0]

    return crit


# ----------------------------------------------------------------
# METHODS - representations
# ----------------------------------------------------------------


def log_critical_points(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    t_min: float = -np.inf,
    t_max: float = np.inf,
    real_valued: bool = False,
) -> str:
    n_der = len(crits) - 1
    classifications = gather_multi_level_critical_points_classifications(
        crits,
        eps=MACHINE_EPS,
        t_min=t_min,
        t_max=t_max,
        real_valued=real_valued,
    )
    data = []
    for t0, classif in classifications:
        class_as_strs = [', '.join([kind.value for kind in kinds]) if len(kinds) > 0 else None for kinds in classif]
        data.append([f'{t0:.6f}'] + class_as_strs)
    table = tabulate(
        data,
        headers=['t/T'] + [f'crit p{"´" * n}' for n in range(n_der + 1)],
        tablefmt='pretty',
        floatfmt='.4f',
        stralign='left',
        missingval='—',
        showindex=False,
        colalign=['right'] + ['center'] * (n_der + 1),
        rowalign='top',
    )
    return table


# ----------------------------------------------------------------
# METHODS - multiple series of critical points
# ----------------------------------------------------------------


def clean_up_critical_points(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    eps: float,
    t_min: float = -np.inf,
    t_max: float = np.inf,
    real_valued: bool = False,
) -> list[list[tuple[float, float, set[EnumCriticalPoints]]]]:
    times_all = [[t0 for t0, y0, kinds in crit] for crit in crits]
    _, assignments = duplicates_get_assignment_dictionaries(
        *times_all,
        eps=eps,
        boundaries_real=(t_min, t_max),
        real_valued=real_valued,
    )
    crits = [
        [
            (t0, crit[indices[0]][1], set().union(*[crit[i][2] for i in indices ]))
            for t0, indices in assignment.items()
        ]
        for assignment, crit in zip(assignments, crits)  # fmt: skip
    ]

    return crits


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def get_time_grid(
    t: list[float],
    eps: float,
    t_min: float,
    t_max: float,
) -> list[float]:
    if len(t) == 0:
        return []
    # removes ε-duplicates + forces values close to boundaries to be on the boundaries
    t, _ = duplicates_get_assignment_maps(t, eps=eps, boundaries_real=(t_min, t_max), real_valued=True)
    t = [tt for tt in t if t_min <= tt and tt <= t_max]
    # ensure finite values:
    t_min = t_min if abs(t_min) < np.inf else min(t)
    t_max = t_max if abs(t_max) < np.inf else max(t)
    # add extra supports and compute differences between successive points:
    dt = 0.1 * max([abs(t0) + 1 for t0 in t])
    delta = np.minimum(
        np.diff([t_min - dt] + t),
        np.diff(t + [t_max + dt]),
    )
    # only use balls that occur in window:
    balls = list(zip(t, delta))
    # compute grid:
    t_end, d_end = balls[-1]
    t_grid = flatten(*[[tt - d / 2, tt] for tt, d in balls], [t_end + d_end / 2])
    return t_grid


def handle_inflection_points(
    crit: list[tuple[float, float, set[EnumCriticalPoints]]]
) -> list[tuple[float, float, set[EnumCriticalPoints]]]:
    minmax = {EnumCriticalPoints.LOCAL_MINIMUM, EnumCriticalPoints.LOCAL_MAXIMUM}
    for k, (t0, y0, kinds) in enumerate(crit):
        if minmax.issubset(kinds):
            kinds = kinds.difference(minmax).union({EnumCriticalPoints.INFLECTION})
            crit[k] = (t0, y0, kinds)
    return crit


def gather_multi_level_critical_points_classifications(
    crits: list[list[tuple[float, float, set[EnumCriticalPoints]]]],
    eps: float,
    t_min: float = -np.inf,
    t_max: float = np.inf,
    real_valued: bool = False,
) -> list[tuple[float, list[set[EnumCriticalPoints]]]]:
    '''
    Consolidates and gathers information about
    '''
    crits = clean_up_critical_points(crits, t_min=t_min, t_max=t_max, eps=eps, real_valued=real_valued)  # fmt: skip

    times, _ = duplicates_get_assignment_maps(
        *[[t0 for t0, y0, kinds in crit if len(kinds) > 0] for crit in crits],
        eps=eps,
        boundaries_real=(t_min, t_max),
        real_valued=True,
    )
    START = [t_min] if abs(t_min) < np.inf else []
    MIDDLE = sorted([t0 for t0 in times if t_min < t0 and t0 < t_max])
    END = [t_max] if abs(t_max) < np.inf else []
    times = START + MIDDLE + END

    classifications = [
        (
            t0,
            [set().union(*[kinds for t0_, y0, kinds in crit if t0_ == t0]) for crit in crits],
        )
        for t0 in times
    ]

    return classifications
