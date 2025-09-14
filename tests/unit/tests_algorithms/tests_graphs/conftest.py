#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import networkx as nx

from tests.unit.thirdparty.unit import *

from src.thirdparty.maths import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope="module")
def graph_non_cyclical_1() -> nx.DiGraph:
    nodes = [a for a in "abcde"]
    edges = [("d", "a"), ("d", "b"), ("d", "e"), ("a", "b"), ("b", "c")]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


@fixture(scope="module")
def graph_non_cyclical_2() -> nx.DiGraph:
    nodes = [a for a in "abcd"]
    edges = [("d", "a"), ("a", "b"), ("b", "c")]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


@fixture(scope="module")
def graph_cyclical_1() -> nx.DiGraph:
    nodes = [a for a in "abcdef"]
    edges = [
        ("e", "f"),
        ("f", "d"),
        ("d", "a"),
        ("d", "b"),
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
    ]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G
