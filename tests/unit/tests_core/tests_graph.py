#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.core.graph import *

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope='function')
def graph_non_cyclical_1() -> tuple[list[str], list[tuple[str, str]]]:
    nodes = [a for a in 'abcde']
    edges = [('d', 'a'), ('d', 'b'), ('d', 'e'), ('a', 'b'), ('b', 'c')]
    return nodes, edges


@fixture(scope='function')
def graph_non_cyclical_2() -> tuple[list[str], list[tuple[str, str]]]:
    nodes = [a for a in 'abcd']
    edges = [('d', 'a'), ('a', 'b'), ('b', 'c')]
    return nodes, edges


@fixture(scope='function')
def graph_cyclical_1() -> tuple[list[str], list[tuple[str, str]]]:
    nodes = [a for a in 'abcdef']
    edges = [('e', 'f'), ('f', 'd'), ('d', 'a'), ('d', 'b'), ('a', 'b'), ('b', 'c'), ('c', 'd')]
    return nodes, edges


# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


def test_compute_ranks(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # fixtures
    graph_non_cyclical_1: tuple[list[str], list[tuple[str, str]]],
    graph_non_cyclical_2: tuple[list[str], list[tuple[str, str]]],
    graph_cyclical_1: tuple[list[str], list[tuple[str, str]]],
):
    r = compute_ranks(*graph_non_cyclical_1)
    test.assertDictEqual(r, {'d': 0, 'a': 1, 'e': 1, 'b': 2, 'c': 3})
    r = compute_ranks(*graph_non_cyclical_2)
    test.assertDictEqual(r, {'d': 0, 'a': 1, 'b': 2, 'c': 3})
    r = compute_ranks(*graph_cyclical_1)
    test.assertTrue(-1 in r.values(), 'Should detect circularity.')
    return


def test_sort_nodes_by_rank(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # fixtures
    graph_non_cyclical_1: tuple[list[str], list[tuple[str, str]]],
    graph_non_cyclical_2: tuple[list[str], list[tuple[str, str]]],
    graph_cyclical_1: tuple[list[str], list[tuple[str, str]]],
):
    nodes, err = sort_nodes_by_rank(*graph_non_cyclical_1)
    test.assertFalse(err, 'Should note non-circularity.')
    test.assertListEqual(nodes[0:][:1], ['d'])
    test.assertListEqual(sorted(nodes[1:3]), ['a', 'e'])
    test.assertListEqual(nodes[3:][:1], ['b'])
    test.assertListEqual(nodes[4:][:1], ['c'])

    nodes, err = sort_nodes_by_rank(*graph_non_cyclical_2)
    test.assertFalse(err, 'Should note non-circularity.')
    test.assertListEqual(nodes[0:][:1], ['d'])
    test.assertListEqual(nodes[1:][:1], ['a'])
    test.assertListEqual(nodes[2:][:1], ['b'])
    test.assertListEqual(nodes[3:][:1], ['c'])

    nodes, err = sort_nodes_by_rank(*graph_cyclical_1)
    test.assertTrue(err, 'Should note circularity.')
    return
