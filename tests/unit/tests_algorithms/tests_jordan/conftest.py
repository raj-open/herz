#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import networkx as nx
import numpy as np

from tests.unit.thirdparty.unit import *

from src.core.utils import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="module")
def graph_directed() -> nx.DiGraph:
    nodes = [a for a in "abcde"]
    edges = [
        ("a", "b"),
        ("a", "c"),
        ("c", "d"),
        ("e", "d"),
    ] + [(a, a) for a in nodes]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


@fixture(scope="module")
def weights(graph_directed: nx.DiGraph) -> NDArray[np.float64]:
    G = graph_directed
    nodes = list(G.nodes)
    N = len(nodes)
    W = np.zeros(shape=(N, N))
    for u, v in G.edges:
        i = nodes.index(u)
        j = nodes.index(v)
        deg_u = len([e for e in G.edges if e[0] == u])
        W[j, i] = 1 / deg_u
    return W


@fixture(scope="module")
def generator(
    weights: NDArray[np.float64],
) -> NDArray[np.float64]:
    W = weights
    N = W.shape[0]
    Id = np.eye(N)
    A = (W - Id).T
    return A


@fixture(scope="module")
def random_jordan_small() -> NDArray[np.float64]:
    eig = [0, 4, 4, -10]
    sizes = [3, 2, 1, 2]
    spec = flatten(*[[t] * sz for t, sz in zip(eig, sizes)])
    D = np.diag(spec)
    m = sum(sizes)
    N = np.zeros((m, m))
    positions = [0, *np.cumsum(sizes).tolist()]
    for i, sz in zip(positions, sizes):
        N[i:, i:][:sz, :sz] = np.eye(sz, k=1)
    A = D + N
    return A


@fixture(scope="module")
def random_jordan() -> NDArray[np.float64]:
    eig = [0, 1, 1, 3, 4, 4, 4, -10]
    sizes = [3, 2, 1, 2, 3, 3, 5, 2]
    spec = flatten(*[[t] * sz for t, sz in zip(eig, sizes)])
    D = np.diag(spec)
    m = sum(sizes)
    N = np.zeros((m, m))
    positions = [0, *np.cumsum(sizes).tolist()]
    for i, sz in zip(positions, sizes):
        N[i:, i:][:sz, :sz] = np.eye(sz, k=1)
    A = D + N
    while True:
        try:
            V = np.random.randn(m, m)
            Vinv = np.linalg.inv(V)
            break

        except Exception as _:
            continue
    # A = V @ A @ Vinv
    return A
