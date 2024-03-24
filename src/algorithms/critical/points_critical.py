#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...core.constants import *
from ...core.utils import *
from ...models.critical import *
from ...models.enums import *
from ...models.epsilon import *
from ...models.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_critical_points',
    'get_critical_points_bounded',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_critical_points(
    p: Poly[float],
    dp: Poly[float],
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[CriticalPoint]:
    eps = p.accuracy
    crit = []

    # necessary condition: t (real-valued) is critical ONLY IF p'(t) = 0
    t_crit = dp.real_roots

    # remove eps-close points
    t_crit, _ = duplicates_get_assignment_maps(t_crit, eps=eps, real_valued=True)
    N = len(t_crit)
    if N == 0:
        return crit

    # compute points between critical points
    t_grid = get_time_grid(t_crit, t_min=t_min, t_max=t_max, eps=eps)

    # classify critical points:
    # FAST METHOD:
    N = len(t_grid)
    values = p.values(t_grid)
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
                crit.append(CriticalPoint(x=t0, y=y0, kinds={EnumCriticalPoints.LOCAL_MINIMUM}))
            case (EnumSign.REAL_POSITIVE, EnumSign.REAL_NEGATIVE):
                crit.append(CriticalPoint(x=t0, y=y0, kinds={EnumCriticalPoints.LOCAL_MAXIMUM}))
            case (EnumSign.REAL_NEGATIVE, EnumSign.REAL_NEGATIVE) | (
                EnumSign.REAL_POSITIVE,
                EnumSign.REAL_POSITIVE,
            ):
                crit.append(CriticalPoint(x=t0, y=y0, kinds={EnumCriticalPoints.INFLECTION}))
            case _:
                # NOTE: This case should not occur! If it does - reject!
                pass

    # add in zeroes
    # NOTE: increase eps-value, to prevent duplicates
    t_zeroes = p.real_roots
    t_zeroes, _ = duplicates_get_assignment_maps(t_zeroes, eps=eps, boundaries_real=(t_min, t_max), real_valued=True)  # fmt: skip
    times = [pt.x for pt in crit]
    for t0 in t_zeroes:
        # NOTE: this is not necessary, as duplicate cleanup is performed later!
        # if len(times) > 0:
        #     i = closest_index(t0, times)
        #     pt = crit[i]
        #     # NOTE: the eps-value should not be too big!
        #     if is_epsilon_eq(pt.x, t0, eps=eps):
        #         crit[i] = CriticalPoint(x=t0, y=0.0, kinds=pt.kinds.union({EnumCriticalPoints.ZERO}))
        #         continue
        crit.append(CriticalPoint(x=t0, y=0.0, kinds={EnumCriticalPoints.ZERO}))

    # deal with inflection points
    crit = handle_inflection_points(crit)

    # sort points
    crit = sorted(crit, key=lambda pt: pt.x)

    return crit


def get_critical_points_bounded(
    p: Poly[float],
    dp: Poly[float],
    t_min: float = 0.0,
    t_max: float = 1.0,
) -> list[CriticalPoint]:
    eps = p.accuracy
    crit = get_critical_points(p=p, dp=dp, t_min=t_min, t_max=t_max)

    if len(crit) == 0:
        return []

    t_crit = [crit[0].x, crit[-1].x]
    values = p.values([t_min, t_max])

    # add in left-boundary or purify points that are too close
    if is_epsilon_eq(t_min, t_crit[0], eps=eps):
        crit[0] = CriticalPoint(x=t_min, y=values[0], kinds=crit[0].kinds)
    else:
        crit.insert(0, CriticalPoint(x=t_min, y=values[0]))

    # add in right-boundary or purify points that are too close
    if is_epsilon_eq(t_max, t_crit[-1], eps=eps):
        crit[-1] = CriticalPoint(x=t_max, y=values[-1], kinds=crit[-1].kinds)
    else:
        t_crit.append(t_max)
        crit.append(CriticalPoint(x=t_max, y=values[-1]))

    # compute absoulte min/max
    values = np.asarray([pt.y for pt in crit])
    y_min = np.min(values)
    y_max = np.max(values)
    for k, pt in enumerate(crit):
        if is_epsilon_eq(y_max, pt.y, eps=MACHINE_EPS):
            crit[k] = CriticalPoint(
                x=pt.x,
                y=y_max,
                kinds=pt.kinds.union({EnumCriticalPoints.MAXIMUM}),
            )
        elif is_epsilon_eq(y_min, pt.y, eps=MACHINE_EPS):
            crit[k] = CriticalPoint(
                x=pt.x,
                y=y_min,
                kinds=pt.kinds.union({EnumCriticalPoints.MINIMUM}),
            )

    # remove points with no classification
    crit = [pt for pt in crit if len(pt.kinds) > 0]

    return crit


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def handle_inflection_points(crit: list[CriticalPoint]) -> list[CriticalPoint]:
    minmax = {EnumCriticalPoints.LOCAL_MINIMUM, EnumCriticalPoints.LOCAL_MAXIMUM}
    for k, pt in enumerate(crit):
        if minmax.issubset(pt.kinds):
            crit[k] = CriticalPoint(
                x=pt.x,
                y=pt.y,
                kinds=pt.kinds.difference(minmax).union({EnumCriticalPoints.INFLECTION}),
            )
    return crit


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
