#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import os
from typing import Callable

import numpy as np

from tests.unit.__paths__ import *
from tests.unit.thirdparty.unit import *

from src.core.log import *
from src.thirdparty.maths import *

# ----------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------

np.seterr(all="warn")

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

configure_logging(
    name="unit",
    level=LOG_LEVELS.INFO,
    path=os.path.join(get_tests_path(), "logs"),
)


@fixture(scope="module", autouse=True)
def test() -> TestCase:
    return TestCase()


@fixture(scope="session", autouse=True)
def seed() -> int:
    seed = 901372893172
    reseed(seed)
    return seed


@fixture(scope="module", autouse=True)
def debug() -> Callable[..., None]:
    """
    Fixture for development purposes only.
    Logs to file 'logs/debug.log'.
    """
    return log_dev
