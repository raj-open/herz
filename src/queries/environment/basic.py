#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from functools import wraps
from typing import Any
from typing import Callable
from typing import Concatenate
from typing import ParamSpec
from typing import TypeVar

from ...thirdparty.system import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "add_environment",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS/VARIABLES
# ----------------------------------------------------------------

PARAMS = ParamSpec("PARAMS")
RETURN = TypeVar("RETURN")

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def add_environment(
    action: Callable[Concatenate[str, dict[str, Any], PARAMS], RETURN],
) -> Callable[Concatenate[str, PARAMS], RETURN]:
    """
    Decorates method to make it get environment first.
    Runs method with error wrapping,
    catching errors with a ValueError
    """

    # modify function
    @wraps(action)
    def wrapped_action(path: str, *_: PARAMS.args, **__: PARAMS.kwargs) -> RETURN:
        try:
            env = get_environment(path=path)
            result = action(path, env, *_, **__)
            return result

        except Exception as _:
            raise ValueError("Create a .env file in the project root with appropriate values!")

    return wrapped_action
