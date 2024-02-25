#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.system import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.core.log import *
from .__paths__ import *

# ----------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------

np.seterr(all='warn')

# ----------------------------------------------------------------
# FIXTURES
# ----------------------------------------------------------------

configure_logging(
    name='unit',
    level=LOG_LEVELS.INFO,
    path=os.path.join(get_tests_path(), 'logs'),
)


@fixture(scope='module', autouse=True)
def test() -> TestCase:
    return TestCase()


@fixture(scope='module', autouse=True)
def debug() -> Callable[..., None]:
    '''
    Fixture for development purposes only.
    Logs to file 'logs/debug.log'.
    '''
    return log_dev


@fixture(scope='module', autouse=True)
def module() -> Callable[[str], str]:
    return get_module
