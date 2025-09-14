#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script to creates the FastAPI instance,
including resources and endpoints.
"""

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from fastapi import FastAPI
from fastapi.security import HTTPBasic
from fastapi_offline import FastAPIOffline

# from fastapi.staticfiles import StaticFiles
from ..setup import *
from .endpoints import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "create_ui",
]


# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def create_ui(debug: bool) -> FastAPI:
    """
    Creates the API and adds endpoints

    **NOTE:** Uses `fastapi-offline` so that can be run offline.
    """
    app = FastAPIOffline(
        title=config.INFO.name.title(),
        description=config.INFO.description,
        version=config.INFO.version,
        debug=debug,
        # see https://fastapi.tiangolo.com/how-to/configure-swagger-ui
        # and https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": 0,
            "displayRequestDuration": True,
            "syntaxHighlight": True,
            "syntaxHighlight.theme": "obsidian",
        },
    )
    add_resources(app)
    add_endpoints(app)
    return app


def add_resources(app: FastAPI):
    """
    Connects static resources.
    """
    # app.mount('/index.html', StaticFiles(directory='src/python/ui/static', html=True), name='nodejs')
    return


def add_endpoints(app: FastAPI):
    """
    Sets all the endpoints for the API.
    """
    sec_http = HTTPBasic()
    add_endpoints_basic(app, tag="Basic", sec=sec_http)
    add_endpoints_features(app, tag="Features", sec=sec_http)
    return
