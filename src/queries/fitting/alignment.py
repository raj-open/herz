#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.data import *
from ...thirdparty.maths import *
from ...thirdparty.types import *

from ...models.fitting import *
from ...models.polynomials import *
from ...models.intervals import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_realignment_intervals',
    'get_realignment_special',
    'get_realignment_polynomial',
    'get_realignment_trig',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_realignment_intervals(
    intervals: Iterable[tuple[float, float]],
    special: dict[str, SpecialPointsConfig],
    info: FittedInfoNormalisation,
    collapse: bool,
) -> list[tuple[float, float]]:
    t_align = special['align'].time
    period = info.period
    intervals = [(a - t_align, b - t_align) for a, b in intervals]
    if collapse:
        intervals = collapse_intervals_to_cycle(intervals, offset=0, period=period)
    return intervals


def get_realignment_special(
    special: dict[str, SpecialPointsConfig],
    info: FittedInfoNormalisation,
):
    '''
    Realigns special points.
    '''
    T = info.period
    t_align = special['align'].time
    for key, point in special.items():
        if key == 'align':
            continue
        t = point.time
        point.time = (t - t_align) % T
    return special


def get_realignment_polynomial(
    p: Poly[float],
    special: dict[str, SpecialPointsConfig],
) -> Poly[float]:
    '''
    Realigns polynomial to start at a particular timepoint.
    Preserves periodicity.
    '''
    t_align = special['align'].time
    p = p.rescale(t0=t_align)
    # NOTE: the rescale method automatically corrects the offset-value
    # preserving the cyclic nature of the polynomial model.
    # Hence the following line is not necessary:
    # p.offset = -t_align
    return p


def get_realignment_trig(
    fit: FittedInfoTrig,
    special: dict[str, SpecialPointsConfig],
) -> FittedInfoTrig:
    '''
    Realigns trigonometric model to start at a particular timepoint.
    '''
    t_align = special['align'].time
    fit = fit.model_copy(deep=True)
    # NOTE: cannot perform "mod T", since the cycles have nothing to do with each other!
    fit.hshift = fit.hshift - t_align
    return fit
