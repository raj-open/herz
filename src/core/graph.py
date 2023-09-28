#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.maths import *
from ..thirdparty.types import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'compute_ranks',
    'sort_nodes_by_rank',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOCAL VARIABLES / CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

T = TypeVar('T')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS - rank
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def sort_nodes_by_rank(nodes: list[T], edges: list[tuple[T, T]]) -> tuple[list[T], bool]:
    ranks = compute_ranks(nodes=nodes, edges=edges)
    err = any([r == -1 for r in ranks.values()])
    nodes = sorted(nodes, key=lambda u: ranks[u])
    return nodes, err


def compute_ranks(nodes: list[T], edges: list[tuple[T, T]]) -> dict[T, int]:
    pred = {v: [u for u, v_ in edges if v_ == v] for v in nodes}
    ranks = {u: compute_rank(u, pred=pred) for u in nodes}
    return ranks


def compute_rank(u: T, pred: dict[str, list[T]], upstream: list[T] = []) -> int:
    if u in upstream:
        return -1
    if len(upstream) == 0:
        upstream = [u]
    r = 0
    for uu in pred[u]:
        r_ = compute_rank(uu, pred=pred, upstream=upstream + [u])
        if r_ == -1:
            r = -1
            break
        r = max(r_ + 1, r)
    return r
