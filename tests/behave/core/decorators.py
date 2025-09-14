#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from thirdparty.behave import *

from thirdparty.code import *
from thirdparty.system import *
from thirdparty.types import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "add_data_from_context",
    "add_webdriver_from_context",
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS/VARIABLES
# ----------------------------------------------------------------

PARAMS = ParamSpec("PARAMS")
RETURN = TypeVar("RETURN")

# ----------------------------------------------------------------
# DECORATORS
# ----------------------------------------------------------------


def add_data_from_context(
    action: Callable[
        Concatenate[
            Context,
            UserData,
            PARAMS,
        ],
        RETURN,
    ],
) -> Callable[Concatenate[Context, PARAMS], RETURN]:
    """
    Decorates method by automatically adding

    - userdata

    from the context then carrying out the desired action.
    """

    # modify function
    @wraps(action)
    def wrapped_action(ctx: Context, *_: PARAMS.args, **__: PARAMS.kwargs):
        userdata: UserData = ctx.config.userdata
        result = action(ctx, userdata, *_, **__)
        return result

    return wrapped_action


def add_webdriver_from_context(
    action: Callable[
        Concatenate[
            Context,
            UserData,
            behave_webdriver.Chrome,
            PARAMS,
        ],
        RETURN,
    ],
) -> Callable[Concatenate[Context, PARAMS], RETURN]:
    """
    Decorates method by automatically adding

    - userdata
    - webdriver
    - a list of running processes

    from the context then carrying out the desired action.
    """

    # modify function
    @wraps(action)
    def wrapped_action(ctx: Context, *_: PARAMS.args, **__: PARAMS.kwargs):
        userdata: UserData = ctx.config.userdata
        if "www" not in userdata:
            www = behave_webdriver.Chrome()
            headless = userdata["headless"]
            userdata["www"] = www.headless() if headless else www
        www: behave_webdriver.Chrome = userdata["www"]
        result = action(ctx, userdata, www, *_, **__)
        return result

    return wrapped_action
