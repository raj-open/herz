#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
API endpoints for running endpoints of programme.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.fastapi import *
from ...thirdparty.types import *

from ...setup import config
from ...models.app import *
from ...models.user import *
from ...endpoints import run
from .decorators import *
from .common import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'add_endpoints_run',
]

# ----------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------


def add_endpoints_run(
    app: FastAPI,
    tag: str,
):
    @app.get(
        '/requests/{endpoint}',
        summary='Run an endpoint of the main programme',
        tags=[tag],
    )
    @add_http_auth
    @catch_internal_server_error
    async def method(
        # DEV-NOTE: add for @add_http_auth-decorator
        http_cred: Annotated[HTTPBasicCredentials, FastAPIDepends(get_security())],
        # end of decorator arguments
        payload: Annotated[
            RequestsConfig, FastAPIBody(media_type='application/json;charset=utf-8')
        ],
    ):
        cfg = config.load_internal_config()
        for request in payload.root:
            run.process(cfg=cfg, request=request)
        return PlainTextResponse(status_code=200)

    return
