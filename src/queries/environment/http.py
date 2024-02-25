#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ...thirdparty.types import *

from .basic import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'get_http_ip',
    'get_http_port',
    'get_http_user',
    'get_http_password',
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
    default: str = '0.0.0.0',
) -> str:
    return env.get('HTTP_IP', default)


@add_environment
def get_http_port(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
    default: int = 80,
) -> int:
    value = env.get('HTTP_PORT', default)
    return int(value)


@add_environment
def get_http_user(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
    default: str = 'admin',
) -> str:
    '''
    Gets http user.
    If value not set in .env, will raise a (Key)Exception.
    '''
    value = env['HTTP_USER']
    return value


@add_environment
def get_http_password(
    # DEV-NOTE: from decorator
    path: str,
    env: dict[str, Any],
    # end decorator args
) -> SecretStr:
    '''
    Gets http password.
    If value not set in .env, will raise a (Key)Exception.
    '''
    value = env['HTTP_PASSWORD']
    return SecretStr(value)
