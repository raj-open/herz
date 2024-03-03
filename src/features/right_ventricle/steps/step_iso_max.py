#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ....thirdparty.data import *
from ....thirdparty.maths import *
from ....thirdparty.types import *

from ....core.log import *
from ....core.poly import *
from ....models.app import *
from ....models.enums import *
from ....models.user import *
from ....models.fitting import *
from ....queries.fitting import *
from ....algorithms.cycles import *
from ....algorithms.fit import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'step_iso_max',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def step_iso_max(
    data: pd.DataFrame,
    points: list[tuple[tuple[int, int], dict[str, int]]],
    quantity: str,
) -> None:
    log_warn('Not yet implemented')
    return
