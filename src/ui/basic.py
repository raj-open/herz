#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Main script to creates the FastAPI instance,
including resources and endpoints.
'''

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.fastapi import *

from ..setup import config
from .endpoints import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'create_ui',
]


# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def create_ui(debug: bool) -> FastAPI:
    '''
    Creates the API and adds endpoints

    **NOTE:** Uses `fastapi-offline` so that can be run offline.
    '''
    app = FastAPIOffline(
        title=config.INFO.name.title(),
        description=config.INFO.description,
        version=config.INFO.version,
        debug=debug,
        # see https://fastapi.tiangolo.com/how-to/configure-swagger-ui
        # and https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration
        swagger_ui_parameters={
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 0,
            'displayRequestDuration': True,
            'syntaxHighlight': True,
            'syntaxHighlight.theme': 'obsidian',
        },
    )
    add_resources(app)
    add_endpoints(app)
    return app


def add_resources(app: FastAPI):
    '''
    Connects static resources.
    '''
    # app.mount('/index.html', StaticFiles(directory='src/ui/static', html=True), name='ui')
    return


def add_endpoints(app: FastAPI):
    '''
    Sets all the endpoints for the API.
    '''
    add_endpoints_basic(app, tag='Basic')
    add_endpoints_run(app, tag='Endpoints for main programme')
    return
