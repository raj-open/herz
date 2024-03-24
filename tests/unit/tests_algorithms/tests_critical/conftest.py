#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.core.constants import *
from tests.unit.thirdparty.unit import *

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------


@fixture(scope='module', autouse=True)
def eps() -> float:
    return POLY_RESOLUTION
