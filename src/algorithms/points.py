#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.maths import *

from ..core.log import *
from ..core.constants import *
from ..core.graph import *
from ..core.crit import *
from ..core.poly import *
from ..models.fitting import *
from ..models.enums import *
from ..models.app import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'recognise_special_points',
    'sort_special_points_specs',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def sort_special_points_specs(points: dict[str, SpecialPointsConfig]) -> list[tuple[str, SpecialPointsConfig]]:
    nodes = points.keys()
    points_with_specs = [(key, point) for key, point in points.items() if point.spec is not None]
    edges = [
        (u1, u2)
        for u1, point1 in points_with_specs
        for u2, point2 in points_with_specs
        if (u1 in point2.spec.after) or (u2 in point1.spec.before)
    ]
    nodes, err = sort_nodes_by_rank(nodes, edges)
    if err:
        log_warn('Conditions specified are circular and may therefore be unsatisfiable.')

    return [(u, points[u]) for u in nodes]


def recognise_special_points(
    info: FittedInfo,
    points: list[tuple[str, SpecialPointsConfig]],
    real_valued: bool = False,
) -> dict[str, SpecialPointsConfig]:
    '''
    NOTE: The conditions 'before' / 'after' are defined purely
    in terms of the peak-to-peak cycle.
    '''
    if len(points) == 0:
        return {}

    results = {key: point for key, point in points}
    times = {}
    n_der = max([point.spec.derivative for _, point in points if point.spec is not None])
    # q = get_unnormalised_polynomial_values_only(info)
    q = info.coefficients

    # Get polynomial coefficients of n-th derivatives of curve.
    # NOTE: dx[k] = coeff's of k-th derivative of polynomial x(t)
    dx: list[list[float]] = [[]] * (n_der + 2)
    dx[0] = q
    for k in range(n_der + 1):
        dx[k + 1] = get_derivative_coefficients(dx[k])

    # compute and classify critical points of derivatives:
    crits = [
        get_critical_points_bounded(p=dx[k], dp=dx[k + 1], t_min=0.0, t_max=1.0, eps=FLOAT_ERR)
        for k in range(n_der + 1)
    ]

    # clean up critical points
    crits = clean_up_critical_points(crits, t_min=0.0, t_max=1.0, eps=FLOAT_ERR, real_valued=real_valued)  # fmt: skip

    # determine peak
    crit = filter_kinds(crits[0], kinds={EnumCriticalPoints.MAXIMUM})
    crit = filter_times(crit, t_before=1.0)
    assert len(crit) >= 1, 'The cycle should have exactly one peak!'
    t_max = crit[0][0]

    # shift cycle to format peak-to-peak:
    crits = [[((t - t_max) % 1, y, kinds) for t, y, kinds in crit] for crit in crits]

    # sort critical points:
    crits = [sorted(crit, key=lambda obj: obj[0]) for crit in crits]

    # messages
    log_debug('Critical points of polynomial computed:')
    log_debug_wrapped(lambda: log_critical_points(crits=crits, t_min=0.0, t_max=1.0))
    log_debug(f'Searching for {" -> ".join([ key for key, _ in points ])}.')

    # iteratively identify points:
    for key, point in results.items():
        point.found = False

    for key, point in points:
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
            t0 = crit[0][0]
            times[key] = t0
            log_debug(f'({key}) found t={t0:.4f}·T.')
            # unshift time-values to original format of cycle and store
            results[key].time = (t0 + t_max) % 1
            results[key].found = True
        except:
            log_warn(f'Could not find ({key})!')
            results[key].found = False

    return results


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def filter_kinds(
    crit: list[tuple[float, float, set[EnumCriticalPoints]]], kinds: set[EnumCriticalPoints]
) -> list[list[tuple[float, float, set[EnumCriticalPoints]]]]:
    return [(t0, y0, kinds_) for t0, y0, kinds_ in crit if len(kinds.intersection(kinds_)) > 0]


def filter_times(
    crit: list[tuple[float, float, EnumCriticalPoints]],
    t_after: float = -np.inf,
    t_before: float = np.inf,
):
    return [(t0, y0, kinds) for t0, y0, kinds in crit if t_after < t0 and t0 < t_before]
