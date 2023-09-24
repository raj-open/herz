#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from ..thirdparty.config import *
from ..thirdparty.code import *

from ..paths import *
from ..core.log import *
from ..models.app import *
from ..models.user import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'UNITS',
    'VERSION',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PATH_VERSION = 'dist/VERSION'
PATH_ASSETS_CONFIG_USER = 'setup/config.yaml'
PATH_ASSETS_CONFIG_API = f'{get_source_path()}/setup/config.yaml'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def set_user_config(path: str):
    global PATH_ASSETS_CONFIG_USER
    global USER_CONFIG
    global BASIC
    global DATA_CONFIG
    global OUTPUT_CONFIG
    global LOG_LEVEL

    PATH_ASSETS_CONFIG_USER = path

    USER_CONFIG = load_assets_config(path=PATH_ASSETS_CONFIG_USER)
    BASIC = lazy(lambda x: x.basic, USER_CONFIG)
    DATA_CONFIG = lazy(lambda x: x.data, USER_CONFIG)
    OUTPUT_CONFIG = lazy(lambda x: x.output, USER_CONFIG)
    LOG_LEVEL = lazy(lambda x: x.log_level.name, BASIC)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LAZY LOADED RESOURCES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def load_version(path: str) -> str:
    with open(path, 'r') as fp:
        lines = fp.readlines()
    return ''.join(lines).strip()


@make_lazy
def load_api_info(path: str, version: str) -> AppInfo:
    with open(path, 'r') as fp:
        assets = yaml_to_py_dictionary(yaml.load(fp, Loader=yaml.FullLoader), deep=True)
        assert isinstance(assets, dict)
        api_config: AppConfig = catch_fatal(lambda: AppConfig(**assets))
        api_info = api_config.info
        api_info.version = version
        return api_info


@make_lazy
def load_assets_config(path: str) -> UserConfig:
    with open(path, 'r') as fp:
        assets = yaml_to_py_dictionary(yaml.load(fp, Loader=yaml.FullLoader), deep=True)
        assert isinstance(assets, dict)
        return catch_fatal(lambda: UserConfig(**assets))


# use lazy loading to ensure that values only loaded (once) when used
VERSION = load_version(path=PATH_VERSION)
API_INFO = load_api_info(path=PATH_ASSETS_CONFIG_API, version=VERSION)
UNITS: AppUnits = lazy(lambda x: x.units, API_INFO)
USER_CONFIG = load_assets_config(path=PATH_ASSETS_CONFIG_USER)
BASIC: UserBasicOptions = lazy(lambda x: x.basic, USER_CONFIG)
DATA_CONFIG: UserData = lazy(lambda x: x.data, USER_CONFIG)
PROCESS_CONFIG: UserProcessing = lazy(lambda x: x.processing, USER_CONFIG)
OUTPUT_CONFIG: UserOutput = lazy(lambda x: x.output, USER_CONFIG)
LOG_LEVEL: str = lazy(lambda x: x.log_level.name, BASIC)
