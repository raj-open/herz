#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

# for modifications
from enum import Enum

import requests
from requests import Response
from requests.auth import HTTPBasicAuth

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


class MimeType(Enum):
    BYTES = "application/octet-stream"
    TEXT = "text/plain;charset=utf-8"
    JSON = "application/json;charset=utf-8"
    # see https://learn.microsoft.com/previous-versions/office/office-2007-resource-kit/ee309278(v=office.12)
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    YAML = "application/yaml;charset=utf-8"


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "HTTPBasicAuth",
    "MimeType",
    "Response",
    "requests",
]
