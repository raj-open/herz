#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import Any

from tests.unit.thirdparty.unit import *

from src.core.log import *

# ----------------------------------------------------------------
# LOCAL VARIABLES / CONSTANTS
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

#

# ----------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------


@mark.parametrize(
    ("level",),
    [
        ("INFO",),
        (LOG_LEVELS.INFO,),
        ("DEBUG",),
        (LOG_LEVELS.DEBUG,),
    ],
)
def test_log_configure(
    test: TestCase,
    # test parameters
    level: Any,
):
    with does_not_raise():
        configure_logging(name="unit", level=LOG_LEVELS.DEBUG, path=None)
    return
