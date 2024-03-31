#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import AwareDatetime

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'MetaData',
]

# ----------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------


class MetaData(BaseModel):
    '''
    Meta data of file
    '''

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
    )
    path: str = Field(..., description='Full path to file (directory + filename incl. extension).')
    filename: str = Field(..., description='Filename (without path, but with extension).')
    basename: str = Field(..., description='Filename without path and without extension.')
    ext: str = Field(..., description='Extension of file.')
    size: int = Field(..., description='Size of file in bytes')
    time_created: Optional[AwareDatetime] = Field(None, alias='time-created')
    time_updated: Optional[AwareDatetime] = Field(None, alias='time-updated')
