#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...models.apis import *
from ...models.filesmanager import *
from ...thirdparty.misc import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "get_files_manager",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def get_files_manager(
    location: EnumFilesManagementSystem,
    tz: timezone,
) -> FilesManager:
    """
    Obtains files manager from user choice of system location.
    """
    match location:
        case EnumFilesManagementSystem.OS, _:
            return OSFilesManager(tz=tz)

        case _ as loc, _ if isinstance(loc, EnumFilesManagementSystem):
            raise ValueError(f"No method determined for files system manager `{loc.value}`.")

        case _ as value, _:
            raise ValueError(f"No method determined for files system manager `{value}`.")
