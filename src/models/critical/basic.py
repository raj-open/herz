#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from ..enums import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'CriticalPoint',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


class CriticalPoint(BaseModel):
    '''
    Critical points
    '''

    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )
    x: float
    y: float
    kinds: set[EnumCriticalPoints] = Field(..., default_factory=set)
