#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from typing import Any

from ...models.apis import *
from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "get_http_credentials",
    "get_http_ip",
    "get_http_port",
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


@add_environment
def get_http_ip(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
    default: str = "0.0.0.0",
) -> str:
    return env.get("HTTP_IP", default)


@add_environment
def get_http_port(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
    default: int = 80,
) -> int:
    value = env.get("HTTP_PORT", default)
    return int(value)


@add_environment
def get_http_credentials(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
) -> Credentials:
    """
    Gets http user + token.
    If value not set in .env, will raise a (Key)Exception.
    """
    return Credentials(username=env["HTTP_USER"], token=env["HTTP_PASSWORD"])
