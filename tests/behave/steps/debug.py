#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Just contains steps for debugging purposes only.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from core.decorators import *
from thirdparty.behave import *

from core.log import *
from thirdparty.system import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "given_comment",
    "given_nothing",
    "given_read",
    "given_time_passed",
    "then_comment",
    "then_echo",
    "then_nothing",
    "when_comment",
]

# ----------------------------------------------------------------
# GIVEN, WHEN, THEN
# ----------------------------------------------------------------


@behave.given("% {comment}")
def given_comment(ctx: Context, comment: str):
    """
    Does nothing - treated as comment
    """
    return


@behave.when("% {comment}")
def when_comment(ctx: Context, comment: str):
    """
    Does nothing - treated as comment
    """
    return


@behave.then("% {comment}")
def then_comment(ctx: Context, comment: str):
    """
    Does nothing - treated as comment
    """
    return


@behave.given("nothing happened")
def given_nothing(
    ctx: Context,
):
    """
    **NOTE:** For debugging purposes only.

    A behavioural step, in which nothing happens.
    """
    return


@behave.then("nothing should happen")
def then_nothing(
    ctx: Context,
):
    """
    **NOTE:** For debugging purposes only.

    A behavioural step, in which nothing happens.
    """
    return


@behave.given("{n:d} seconds have passed")
def given_time_passed(
    ctx: Context,
    n: int,
):
    sleep(n)
    return


@behave.given('read "{value}"')
@add_data_from_context
def given_read(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    value: str,
):
    """
    **NOTE:** For debugging purposes only.

    A behavioural step, in which value stored.
    """
    userdata["value"] = value
    return


@behave.then('echo "{value}"')
@add_data_from_context
def then_echo(
    ctx: Context,
    # DEV-NOTE: from decorator
    userdata: UserData,
    # end decorator args
    value: str,
):
    """
    **NOTE:** For debugging purposes only.

    A behavioural step, in which a value is just echoed.

    See `tests/behave/logs/debug.log`.
    """
    value_previous = userdata.get("value", None)
    expr = f"{value_previous} -> {value}"
    log_dev(expr)
    return
