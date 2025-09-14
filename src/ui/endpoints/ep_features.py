#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API endpoints for main features.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...features import *
from ...models.user import *
from ...setup import *
from ...thirdparty.fastapi import *
from ...thirdparty.types import *
from ...thirdparty.web import *
from .decorators import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "add_endpoints_features",
]

# ----------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------


def add_endpoints_features(
    app: FastAPI,
    tag: str,
    sec: HTTPBasic,
):
    """
    Adds endpoints pertaining to the features of the repo.
    """
    # manager_os = user.get_files_manager(
    #     location=EnumFilesManagementSystem.OS,
    #     tz=config.TIMEZONE,
    # )

    @app.post(
        f"/feature/{EnumFeature.RIGHT_VENTRICLE.value}",
        summary=f"Runs the {EnumFeature.RIGHT_VENTRICLE.value} feature",
        tags=[tag],
        include_in_schema=True,
    )
    @catch_internal_server_error
    async def method(
        request: Annotated[RequestConfig, FastAPIBody(media_type=MimeType.YAML.value)],
    ):
        # cfg = config.API_CONFIG
        # run.process(cfg=cfg, request=request)
        return HTMLResponse(
            status_code=200,
            content="""
            <html>
                <head>
                <title>Result</title>
                </head>
                <body>
                    <h1>Under construction</h1>
                </body>
            </html>
            """,
        )
