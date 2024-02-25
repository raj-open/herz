#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.code import *
from ...thirdparty.fastapi import *
from ...thirdparty.types import *

from ...core.log import *
from ...guards.http import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'catch_internal_server_error',
    'add_http_auth',
]

# ----------------------------------------------------------------
# LOCAL CONSTANTS/VARIABLES
# ----------------------------------------------------------------

T1 = TypeVar('T1')
T2 = TypeVar('T2')
PARAMS = ParamSpec('PARAMS')
RETURN = TypeVar('RETURN')

# ----------------------------------------------------------------
# DECORATORS
# ----------------------------------------------------------------


def catch_internal_server_error(
    action: Callable[
        PARAMS,
        Awaitable[RETURN],
    ],
):
    '''
    Decorates and endpoint by returning internal server error if error occurs.
    '''

    # modify function
    @wraps(action)
    async def wrapped_action(
        *_: PARAMS.args,
        **__: PARAMS.kwargs,
    ) -> Awaitable[RETURN]:
        try:
            output = await action(*_, **__)
            return output

        except Exception as err:
            log_error(err)
            raise HTTPException(status_code=500, detail=str(err))

    return wrapped_action


def add_http_auth(
    action: Callable[
        Concatenate[HTTPBasicCredentials, PARAMS],
        Awaitable[RETURN],
    ],
):
    '''
    Decorates and endpoint by adding basic http-authorisation to it.

    **DEV-NOTE:**
    Signature cannot change when using `FastAPI`'s
    `@app.get`, `@app.post`, etc. decorators.
    Thus need to include all arguments needed by our decorators,
    even if superfluous inside undecorated part.
    '''

    # modify function - but with different signature!
    @wraps(action)
    async def wrapped_action(
        http_cred: HTTPBasicCredentials,
        *_: PARAMS.args,
        **__: PARAMS.kwargs,
    ) -> Awaitable[RETURN]:
        try:
            guard_http_credentials(http_cred)

        except Exception as err:
            log_error(err)
            raise HTTPException(status_code=401, detail=str(err))

        output = await action(http_cred, *_, **__)
        return output

    return wrapped_action
