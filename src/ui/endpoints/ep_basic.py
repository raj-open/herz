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

from ...setup import *
from .decorators import *

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
    sec: HTTPBasic,
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
        '/version',
        summary='Display the VERSION of the programme',
        tags=[tag],
        include_in_schema=True,
    )
    @catch_internal_server_error
    async def method():
        return PlainTextResponse(status_code=200, content=config.VERSION)

    @app.get(
        '/ping',
        summary='Ping api',
        tags=[tag],
        include_in_schema=True,
    )
    @add_http_auth
    @catch_internal_server_error
    async def method(
        http_cred: Annotated[HTTPBasicCredentials, FastAPIDepends(sec)],
        # end of decorator arguments
    ):
        '''
        An endpoint for debugging.
        '''
        return PlainTextResponse(status_code=200, content=f'Server running!')
