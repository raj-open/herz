#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from itertools import pairwise

import numpy as np

from ...core.constants import *
from ...core.log import *
from ...models.app import *
from ...models.critical import *
from ...models.enums import *
from ...models.fitting import *
from ...models.polynomials import *
from ...thirdparty.maths import *
from ..graph import *
from .clean import *
from .logging import *
from .points_critical import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "recognise_special_points",
    "sort_special_points_specs",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def sort_special_points_specs(
    points: dict[str, SpecialPointsConfig],
) -> list[tuple[str, SpecialPointsConfig]]:
    nodes = points.keys()
    points_with_specs = [
        (key, point) for key, point in points.items() if point.spec is not None
    ]
    edges = [
        (u1, u2)
        for u1, point1 in points_with_specs
        for u2, point2 in points_with_specs
        if (u1 in point2.spec.after) or (u2 in point1.spec.before)
    ]
    nodes, err = sort_nodes_by_rank(nodes, edges)
    if err:
        log_warn("Conditions specified are circular and may therefore be unsatisfiable.")

    return [(u, points[u]) for u in nodes]


def recognise_special_points(
    poly: Poly[float],
    search: list[tuple[str, SpecialPointsConfig]],
    skip_errors: bool,
) -> dict[str, SpecialPointsConfig]:
    """
    NOTE: The conditions 'before' / 'after' are defined purely
    in terms of the peak-to-peak cycle.
    """
    if len(search) == 0:
        return {}

    results = {key: point for key, point in search}
    times = {}
    n_der = max([point.spec.derivative for _, point in search if point.spec is not None])

    # create a non-cyclic copy of the polynomial (preserve all else)
    q = Poly[float](coeff=poly.coefficients, accuracy=poly.accuracy)

    # Get n-th derivatives of polynomial.
    polys = [q]
    for _ in range(n_der + 1):
        q = q.derivative()
        polys.append(q)

    # compute and classify critical points of derivatives:
    crits = [
        get_critical_points_bounded(p=q, dp=dq, t_min=0.0, t_max=1.0)
        # DEV-NOTE: equivalent to zip(polys, polys[1:])
        for q, dq in pairwise(polys)
    ]

    # clean up critical points
    crits = clean_up_critical_points(crits, t_min=0.0, t_max=1.0, eps=FLOAT_ERR)  # fmt: skip

    # determine peak
    crit = filter_kinds(crits[0], kinds={EnumCriticalPoints.MAXIMUM})
    crit = filter_times(crit, t_before=1.0)
    assert len(crit) >= 1, f"The cycle has {len(crit)} peaks but should have exactly one!"
    t_max = crit[0].x

    # shift cycle to format peak-to-peak (NOTE: period scaled to 1)
    crits = [
        [CriticalPoint(x=(pt.x - t_max) % 1, y=pt.y, kinds=pt.kinds) for pt in crit]
        for crit in crits
    ]

    # sort critical points:
    crits = [sorted(crit, key=lambda pt: pt.x) for crit in crits]

    # messages
    log_debug("Critical points of polynomial computed:")
    log_debug_wrapped(
        lambda: log_critical_points(crits=crits, t_min=0.0, t_max=1.0, polys=polys)
    )
    log_debug(f"Searching for {' -> '.join([key for key, _ in search])}.")

    # iteratively identify points:
    for key, point in results.items():
        point.found = False

    for key, point in search:
        spec = point.spec
        if spec is None:
            continue
        n = spec.derivative

        # determine preceeding times / successor times
        # NOTE: if point is not defined, default to start / end
        t_after = 0.0 if spec.strict else -np.inf
        t_before = 1.0 if spec.strict else np.inf

        t_after = max([t_after] + [times.get(key_, t_after) for key_ in spec.after])
        t_before = min([t_before] + [times.get(key_, t_before) for key_ in spec.before])

        # find critical point
        log_debug(f'({key}) search for {t_after:.4f} < t/T < {t_before:.4f} s.t. p{"´" * n} @ t is {spec.kind.value}.')  # fmt: skip

        crit = filter_kinds(crits[n], kinds={spec.kind})
        crit = filter_times(crit, t_after=t_after, t_before=t_before)

        try:
            t0 = crit[0].x
            times[key] = t0
            log_debug(f"({key}) found t={t0:.4f}·T.")
            # unshift time-values to original format of cycle and store
            t = (t0 + t_max) % 1
            x = poly(t)
            results[key].time = t
            results[key].value = x
            results[key].found = True

        except Exception as err:
            results[key].found = False
            crit = filter_times(crits[n], t_after=t_after, t_before=t_before)
            crit = filter_kinds(crits[n], kinds={spec.kind})
            crit = filter_times(crit, t_after=t_after, t_before=t_before)
            if skip_errors:
                log_warn(f'Could not find special point "{key}"! (non critical)')
            else:
                log_error(f'Could not find special point "{key}"!')
                # raise err

    return results


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def filter_kinds(
    crit: list[CriticalPoint],
    kinds: set[EnumCriticalPoints],
) -> list[CriticalPoint]:
    return [pt for pt in crit if len(kinds.intersection(pt.kinds)) > 0]


def filter_times(
    crit: list[tuple[float, float, EnumCriticalPoints]],
    t_after: float = -np.inf,
    t_before: float = np.inf,
) -> list[CriticalPoint]:
    return [pt for pt in crit if t_after < pt.x and pt.x < t_before]
