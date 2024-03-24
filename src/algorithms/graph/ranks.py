#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.maths import *
from ...thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'DiGraphExtra',
    'sort_nodes_by_rank',
]

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

T = TypeVar('T')

# ----------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------


class DiGraphExtra(Generic[T], nx.DiGraph):
    def __init__(self, nodes: Iterable[T], edges: Iterable[tuple[T, T]], **__):
        super().__init__(**__)
        self.add_nodes_from(nodes)
        self.add_edges_from(edges)

    @property
    def ranks(self) -> dict[T, int]:
        return {u: self.rank(u) for u in self.nodes}

    def rank(self, u: T, upstream: list[T] = []):
        if u in upstream:
            return -1
        if len(upstream) == 0:
            upstream = [u]
        r = 0
        for uu in self.predecessors(u):
            r_ = self.rank(uu, upstream=upstream + [u])
            if r_ == -1:
                r = -1
                break
            r = max(r_ + 1, r)
        return r


# ----------------------------------------------------------------
# METHODS - rank
# ----------------------------------------------------------------


def sort_nodes_by_rank(
    nodes: Iterable[T],
    edges: Iterable[tuple[T, T]],
) -> tuple[list[T], bool]:
    G = DiGraphExtra[T](nodes, edges)
    ranks = G.ranks
    err = any([r == -1 for r in ranks.values()])
    nodes = sorted(nodes, key=lambda u: ranks[u])
    return nodes, err
