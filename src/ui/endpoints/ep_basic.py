#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
API endpoints basic.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.fastapi import *
from ...thirdparty.types import *

from ...setup import config
from .decorators import *
from .common import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'add_endpoints_basic',
]

# ----------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------


def add_endpoints_basic(
    app: FastAPI,
    tag: str,
):
    '''
    Adds basic endpoints.
    '''

    @app.get(
        '/',
        summary='',
        tags=[tag],
        include_in_schema=False,
    )
    async def method():
        return RedirectResponse('/docs')

    @app.get(
        '/ping',
        summary='Ping the server',
        tags=[tag],
    )
    @add_http_auth
    @catch_internal_server_error
    async def method(
        # DEV-NOTE: add for @add_http_auth-decorator
        http_cred: Annotated[HTTPBasicCredentials, FastAPIDepends(get_security())],
        # end of decorator arguments
        name: str,
    ):
        '''
        An endpoint for debugging.
        '''
        return PlainTextResponse(status_code=200, content=f'Hello, {name}!')

    @app.get(
        '/version',
        summary='Display the version of the programme',
        tags=[tag],
    )
    async def method():
        return PlainTextResponse(status_code=200, content=config.VERSION)

    return
