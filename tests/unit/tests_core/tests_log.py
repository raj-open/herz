#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.log import *
from src.thirdparty.types import *
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
    ('level',),
    [
        ('INFO',),
        (LOG_LEVELS.INFO,),
        ('DEBUG',),
        (LOG_LEVELS.DEBUG,),
    ],
)
def test_log_configure(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    level: Any,
):
    with does_not_raise():
        configure_logging(name='unit', level=LOG_LEVELS.DEBUG, path=None)
    return
