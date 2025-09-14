#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from tests.unit.thirdparty.unit import *

from src.algorithms.graph.ranks import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_compute_ranks(
    test: TestCase,
    # fixtures
    graph_non_cyclical_1: tuple[list[str], list[tuple[str, str]]],
    graph_non_cyclical_2: tuple[list[str], list[tuple[str, str]]],
    graph_cyclical_1: tuple[list[str], list[tuple[str, str]]],
):
    G = graph_non_cyclical_1
    G = DiGraphExtra(G.nodes, G.edges)
    r = G.ranks
    test.assertDictEqual(r, {"d": 0, "a": 1, "e": 1, "b": 2, "c": 3})
    G = graph_non_cyclical_2
    G = DiGraphExtra(G.nodes, G.edges)
    r = G.ranks
    test.assertDictEqual(r, {"d": 0, "a": 1, "b": 2, "c": 3})
    G = graph_cyclical_1
    G = DiGraphExtra(G.nodes, G.edges)
    r = G.ranks
    test.assertTrue(-1 in r.values(), "Should detect circularity.")
    return


def test_sort_nodes_by_rank(
    test: TestCase,
    # fixtures
    graph_non_cyclical_1: tuple[list[str], list[tuple[str, str]]],
    graph_non_cyclical_2: tuple[list[str], list[tuple[str, str]]],
    graph_cyclical_1: tuple[list[str], list[tuple[str, str]]],
):
    G = graph_non_cyclical_1
    nodes, err = sort_nodes_by_rank(nodes=G.nodes, edges=G.edges)
    test.assertFalse(err, "Should note non-circularity.")
    test.assertListEqual(nodes[0:][:1], ["d"])
    test.assertListEqual(sorted(nodes[1:3]), ["a", "e"])
    test.assertListEqual(nodes[3:][:1], ["b"])
    test.assertListEqual(nodes[4:][:1], ["c"])

    G = graph_non_cyclical_2
    nodes, err = sort_nodes_by_rank(nodes=G.nodes, edges=G.edges)
    test.assertFalse(err, "Should note non-circularity.")
    test.assertListEqual(nodes[0:][:1], ["d"])
    test.assertListEqual(nodes[1:][:1], ["a"])
    test.assertListEqual(nodes[2:][:1], ["b"])
    test.assertListEqual(nodes[3:][:1], ["c"])

    G = graph_cyclical_1
    nodes, err = sort_nodes_by_rank(nodes=G.nodes, edges=G.edges)
    test.assertTrue(err, "Should note circularity.")
    return
