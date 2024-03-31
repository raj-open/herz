#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import requests
from requests import Response
from requests.auth import HTTPBasicAuth

# for modifications
from enum import Enum

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


class MimeType(Enum):
    BYTES = 'application/octet-stream'
    TEXT = 'text/plain;charset=utf-8'
    JSON = 'application/json;charset=utf-8'
    # see https://learn.microsoft.com/previous-versions/office/office-2007-resource-kit/ee309278(v=office.12)
    XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    YAML = 'application/x-yaml'


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'HTTPBasicAuth',
    'MimeType',
    'Response',
    'requests',
]
