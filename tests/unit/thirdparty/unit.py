#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import anyio
from contextlib import nullcontext as does_not_raise
from itertools import product as itertools_product
from pytest import fixture
from pytest_lazyfixture import lazy_fixture
from pytest import LogCaptureFixture
from pytest import mark
from pytest import raises as assert_raises
from testfixtures import LogCapture
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import PropertyMock

import numpy as np
from typing import Iterable
from typing import Literal
from typing import Optional

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def assert_arrays_equal(
    x: Iterable,
    y: Iterable,
    message: Optional[str] = None,
):
    x_ = np.asarray(x)
    y_ = np.asarray(y)
    assert x_.shape == y_.shape, (
        message or f'Arrays must be of equal dimension. Recieved {x_.shape} and {y_.shape}.'
    )
    x__ = x_.flatten()
    y__ = y_.flatten()
    assert all([xx == yy for (xx, yy) in zip(x__, y__)]), (
        message or f'Arrays must contain the same objects. Recieved\n    {x_}\nand\n    {y_}.'
    )
    return


def assert_arrays_close(
    x: Iterable,
    y: Iterable,
    eps: float = 1e-10,
    message: Optional[str] = None,
):
    x_ = np.asarray(x)
    y_ = np.asarray(y)
    assert x_.shape == y_.shape, (
        message or f'Arrays must be of equal dimension. Recieved {x_.shape} and {y_.shape}.'
    )
    x__ = x_.flatten()
    y__ = y_.flatten()
    C = (np.linalg.norm(x__) + np.linalg.norm(y__)) / 2 or 1.0
    dist = np.linalg.norm(x__ - y__) / C
    assert dist < eps, (
        message
        or f'Arrays must be sufficiently close. Recieved\n    x={x_}\nand\n    y={y_}\nfor which\n    %∆ = {dist} > {eps}'
    )
    return


def assert_array_zero(
    x: Iterable,
    message: Optional[str] = None,
):
    x_ = np.asarray(x)
    x__ = x_.flatten()
    assert all([xx == 0 for xx in x__]), (
        message or f'All elements in array must be 0. Recieved\n    {x_}'
    )
    return


def assert_array_close_to_zero(
    x: Iterable,
    eps: float = 1e-10,
    message: Optional[str] = None,
):
    x_ = np.asarray(x)
    x__ = x_.flatten()
    dist = np.linalg.norm(x__)
    assert dist < eps, (
        message
        or f'Array must be sufficiently close to 0. Recieved\n    x={x_}\nfor which\n    ‖x‖ = {dist} > {eps}'
    )
    return


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'LogCapture',
    'LogCaptureFixture',
    'MagicMock',
    'PropertyMock',
    'TestCase',
    'anyio',
    'assert_array_close_to_zero',
    'assert_array_zero',
    'assert_arrays_close',
    'assert_arrays_equal',
    'assert_raises',
    'does_not_raise',
    'fixture',
    'itertools_product',
    'lazy_fixture',
    'mark',
    'patch',
]
