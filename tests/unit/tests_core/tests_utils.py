#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.maths import *
from src.thirdparty.types import *
from tests.unit.thirdparty.unit import *

from src.core.utils import *

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
    ('N', 'indices', 'ch'),
    [
        (8, [3, 4, 7], [False, False, False, True, True, False, False, True]),
        (0, [], []),
        (1, [0], [True]),
        (1, [], [False]),
    ],
)
def test_characteristic_function(
    test: TestCase,
    debug: Callable[..., None],
    module: Callable[[str], str],
    # test parameters
    N: int,
    indices: list[int],
    ch: list[bool],
):
    ch_ = where_to_characteristic(indices=indices, N=N)
    test.assertTrue(all(np.equal(ch_, ch)))
    indices_ = characteristic_to_where(ch=ch)
    test.assertEqual(indices_, indices)
    return
