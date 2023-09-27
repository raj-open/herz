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
    'MARKERS',
    'POLY',
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
    global CASES
    global LOG_LEVEL

    PATH_ASSETS_CONFIG_USER = path

    USER_CONFIG = load_assets_config(path=PATH_ASSETS_CONFIG_USER)
    BASIC = lazy(lambda x: x.basic, USER_CONFIG)
    CASES = lazy(lambda x: [case for case in x.cases if not case.ignore], USER_CONFIG)
    LOG_LEVEL = lazy(lambda x: x.log_level.name, BASIC)

    configure_logging(LOG_LEVEL)
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LAZY LOADED RESOURCES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def load_version(path: str) -> str:
    with open(path, 'r') as fp:
        lines = fp.readlines()
    return ''.join(lines).strip()


@make_lazy
def load_api_config(path: str, version: str) -> AppConfig:
    with open(path, 'r') as fp:
        assets = yaml.load(fp, Loader=yaml.FullLoader)
        assert isinstance(assets, dict)
        api_config: AppConfig = catch_fatal(lambda: AppConfig.parse_obj(assets))
        api_config.info.version = version
        return api_config


@make_lazy
def load_assets_config(path: str) -> UserConfig:
    with open(path, 'r') as fp:
        assets = yaml.load(fp, Loader=yaml.FullLoader)
        assert isinstance(assets, dict)
        return catch_fatal(lambda: UserConfig.parse_obj(assets))


# use lazy loading to ensure that values only loaded (once) when used
VERSION = load_version(path=PATH_VERSION)

API_CONFIG = load_api_config(path=PATH_ASSETS_CONFIG_API, version=VERSION)
INFO: AppInfo = lazy(lambda x: x.info, API_CONFIG)
UNITS: dict[str, str] = lazy(lambda x: x.settings.units, API_CONFIG)
POLY: dict[str, PolynomialSetting] = lazy(lambda x: x.settings.polynomial, API_CONFIG)
MARKERS: MarkerConfig = lazy(lambda x: x.settings.markers, API_CONFIG)

USER_CONFIG = load_assets_config(path=PATH_ASSETS_CONFIG_USER)
BASIC: UserBasicOptions = lazy(lambda x: x.basic, USER_CONFIG)
CASES: list[UserCase] = []
LOG_LEVEL: str = 'INFO'
