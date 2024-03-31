#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from fastapi.security import HTTPBasicCredentials

from ..setup import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'guard_http_user',
    'guard_http_password',
    'guard_http_credentials',
]

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def guard_http_user(value: str):
    '''
    A guard which checks if http username is valid.
    '''
    creds = config.http_creds()
    if value != creds.username:
        raise ValueError(f'Invalid http username')
    return


def guard_http_password(value: str):
    '''
    A guard which checks if http password is valid.
    '''
    creds = config.http_creds()
    if value != creds.token.get_secret_value():
        raise ValueError(f'Invalid http password!')
    return


def guard_http_credentials(
    cred: HTTPBasicCredentials,
):
    '''
    A guard which checks if http credentials are valid.
    '''
    try:
        guard_http_user(cred.username)
        guard_http_password(cred.password)
    except Exception as err:
        # msg = str(err)
        msg = 'Invalid http credentials!'
        raise ValueError(msg)
