#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *

from ...models.critical import *
from ...models.epsilon import *
from ...models.polynomials import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'clean_up_critical_points',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def clean_up_critical_points(
    crits: list[list[CriticalPoint]],
    eps: float,
    t_min: float = -np.inf,
    t_max: float = np.inf,
) -> list[list[CriticalPoint]]:
    '''
    Cleans up critical points
    '''

    times_all = [[pt.x for pt in crit] for crit in crits]

    _, assignments = duplicates_get_assignment_dictionaries(
        *times_all,
        eps=eps,
        bounds=(t_min, t_max),
    )

    crits = [
        [
            CriticalPoint(
                x=t0,
                y=crit[indices[0]].y,
                kinds=set().union(*[crit[i].kinds for i in indices ]))
            for t0, indices in assignment.items()
        ]
        for assignment, crit in zip(assignments, crits)  # fmt: skip
    ]

    return crits
