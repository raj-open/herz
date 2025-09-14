#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import fastapi
import uvicorn
from fastapi import Body as FastAPIBody
from fastapi import Depends as FastAPIDepends
from fastapi import FastAPI
from fastapi import File as FastAPIFile
from fastapi import Form as FastAPIForm
from fastapi import HTTPException
from fastapi import Response as FastAPIResponse
from fastapi import UploadFile as FastAPIUploadFile
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi_offline import FastAPIOffline

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "FastAPI",
    "FastAPIBody",
    "FastAPIDepends",
    "FastAPIFile",
    "FastAPIForm",
    "FastAPIOffline",
    "FastAPIResponse",
    "FastAPIUploadFile",
    "FileResponse",
    "HTMLResponse",
    "HTTPBasic",
    "HTTPBasicCredentials",
    "HTTPException",
    "JSONResponse",
    "OAuth2PasswordRequestForm",
    "PlainTextResponse",
    "RedirectResponse",
    "StaticFiles",
    "fastapi",
    "uvicorn",
]
