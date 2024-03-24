#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *
from ...thirdparty.render import *

from ...core.utils import *
from ...core.constants import *
from ...models.critical import *
from ...models.epsilon import *
from ...models.polynomials import *
from .clean import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'log_critical_points',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def log_critical_points(
    crits: list[list[CriticalPoint]],
    t_min: float,
    t_max: float,
    polys: list[Poly[float]],
    real_valued: bool = False,
) -> str:
    n_der = len(crits) - 1
    classifications = gather_multi_level_critical_points_classifications(
        crits,
        eps=POLY_RESOLUTION,
        t_min=t_min,
        t_max=t_max,
        real_valued=real_valued,
    )

    headers = {'time': 't/T'}
    for k in range(n_der + 1):
        p_dash = f'p{"´" * k}'
        headers = headers | {f'kind_{k}': f'crit {p_dash}', f'value_{k}': f'{p_dash}(t)'}

    data = []
    for t0, classif in classifications:
        row = {'time': f'{t0:.6f}'}
        for k, (q, kinds) in enumerate(zip(polys, classif)):
            row = row | {
                f'kind_{k}': ', '.join([kind.value for kind in kinds]) if len(kinds) > 0 else None,
                f'value_{k}': f'{q(t0):.4f}',
            }
        data.append(row)

    table = tabulate(
        data,
        headers=headers,
        tablefmt='pretty',
        floatfmt='.6f',
        stralign='left',
        missingval='—',
        showindex=False,
        colalign=['right'] + flatten(*[['center', 'right']] * (n_der + 1)),
        rowalign='top',
    )
    return table


# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def gather_multi_level_critical_points_classifications(
    crits: list[list[CriticalPoint]],
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
        *[[pt.x for pt in crit if len(pt.kinds) > 0] for crit in crits],
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
            [set().union(*[pt.kinds for pt in crit if pt.x == t0]) for crit in crits],
        )
        for t0 in times
    ]

    return classifications
