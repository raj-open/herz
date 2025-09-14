#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from contextlib import nullcontext as does_not_raise
from itertools import product as itertools_product
from typing import Iterable
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import anyio
import numpy as np
from pytest import LogCaptureFixture
from pytest import fixture
from pytest import mark
from pytest import raises as assert_raises
from testfixtures import LogCapture

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


def assert_array_close_to_zero(
    x: Iterable,
    decimals: float = 7,
    message: Optional[str] = None,
):
    eps = 10**-decimals
    x_ = np.asarray(x)
    x__ = x_.flatten()
    dist = np.linalg.norm(x__)
    message or f"Array must be sufficiently close to 0. Recieved\n    x={x_}\nfor which\n    ‖x‖ = {dist} > 10^-{decimals}"
    assert dist < eps, message
    return


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "LogCapture",
    "LogCaptureFixture",
    "MagicMock",
    "PropertyMock",
    "TestCase",
    "anyio",
    "assert_array_close_to_zero",
    "assert_raises",
    "does_not_raise",
    "fixture",
    "itertools_product",
    "mark",
    "patch",
]
