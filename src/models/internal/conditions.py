#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ...thirdparty.types import *

from ...core.utils import *

# NOTE: foreign import
from ..generated.app import PolyCritCondition
from ..generated.app import PolyDerCondition
from ..generated.app import PolyIntCondition
from ..generated.app import TimeInterval

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'shift_conditions',
    'shift_condition',
    'shift_der_condition',
    'shift_int_condition',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - shifts
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def shift_conditions(
    conds: list[PolyCritCondition | PolyDerCondition | PolyIntCondition],
    t0: float,
) -> list[PolyCritCondition | PolyDerCondition | PolyIntCondition]:
    return flatten(*[shift_condition(cond, t0) for cond in conds])


def shift_condition(
    cond: PolyCritCondition | PolyDerCondition | PolyIntCondition,
    t0: float,
) -> list[PolyCritCondition | PolyDerCondition | PolyIntCondition]:
    if isinstance(cond, PolyDerCondition):
        return shift_der_condition(cond, t0)
    elif isinstance(cond, PolyIntCondition):
        return shift_int_condition(cond, t0)
    # elif isinstance(cond, PolyCritCondition):
    else:
        return [cond]


def shift_der_condition(cond: PolyDerCondition, t0: float) -> list[PolyDerCondition]:
    conds = []
    if cond.time == 1.0:
        pass
    elif cond.time == t0:
        cond_ = cond.copy(deep=True)
        cond_.time = 0.0
        conds.append(cond_)
        cond_ = cond.copy(deep=True)
        cond_.time = 1.0
        conds.append(cond_)
    else:
        cond_ = cond.copy(deep=True)
        cond_.time = (cond.time - t0) % 1
        conds.append(cond_)
    return conds


def shift_int_condition(cond: PolyIntCondition, t0: float) -> PolyIntCondition:
    times = []
    for interval in cond.times:
        t1 = interval.a
        t2 = interval.b
        if t1 == t2:
            continue
        elif t1 > t2:
            s = -1
            t1, t2 = t2, t1
        else:
            s = 1
        t1_new = (t1 - t0) % 1
        t2_new = (t2 - t0) % 1
        if s == -1:
            if t1_new <= t2_new:
                times.append(TimeInterval(a=t2_new, b=t1_new))
            else:
                if t1_new < 1:
                    times.append(TimeInterval(a=1.0, b=t1_new))
                if 0 < t2_new:
                    times.append(TimeInterval(a=t2_new, b=0.0))
        else:
            if t1_new <= t2_new:
                times.append(TimeInterval(a=t1_new, b=t2_new))
            else:
                if t1_new < 1:
                    times.append(TimeInterval(a=t1_new, b=1.0))
                if 0 < t2_new:
                    times.append(TimeInterval(a=0.0, b=t2_new))
    cond = PolyIntCondition(times=times)
    return [cond]
