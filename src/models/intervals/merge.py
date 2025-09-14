#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from collections.abc import Iterable
from typing import Generator

import networkx as nx

from ...thirdparty.maths import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "compute_overlaps",
    "merge_intervals",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def merge_intervals(
    intervals: Iterable[tuple[float, float]],
) -> Generator[tuple[float, float], None, None]:
    """
    Recursively merges all overlapping intervals yielding the simplified intervals.
    """
    for group in compute_overlaps(intervals):
        if len(group) == 0:
            continue
        left = [intervals[i][0] for i in group]
        right = [intervals[i][1] for i in group]
        a = min(left)
        b = max(right)
        if a >= b:
            continue
        yield a, b


def compute_overlaps(
    intervals: Iterable[tuple[float, float]],
) -> Generator[set[int], None, None]:
    """
    Determines groups of indices of intervals that overlap up to transivitiy.
    """
    N = len(intervals)
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for i, (left1, right1) in enumerate(intervals):
        G.add_edge(i, i)
        for j, (left2, right2) in enumerate(intervals[(i + 1) :]):
            if left1 <= right2 and left2 <= right1:
                G.add_edge(i, i + 1 + j)
    for comp in nx.connected_components(G):
        yield frozenset(comp)
