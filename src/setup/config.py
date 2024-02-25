#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from ..thirdparty.config import *
from ..thirdparty.io import *
from ..thirdparty.system import *

from ..__paths__ import *
from ..core.log import *
from ..queries import environment
from ..models.app import *
from ..models.user import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'INFO',
    'VERSION',
]

# ----------------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------------

_PATH_INTERNAL_CONFIG = os.path.join(get_source_path(), 'setup', 'config.yaml')

_PID = None
_PATH_ENV = None
_PATH_LOGGING = None
_PATH_SESSION = None

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def initialise_application(
    name: str,
    pid: int,
    log_pid: str | None = None,
    debug: bool = False,
):
    '''
    Initialises cli execution of application
    '''
    # initialise logging
    level = LOG_LEVELS.DEBUG if debug else LOG_LEVELS.INFO
    path = _PATH_LOGGING or ''
    configure_logging(name=name, level=level.name, path=path)
    # store pid as single value
    path = log_pid or ''
    if path != '':
        path = get_path_in_session(path)
        create_file_if_not_exists(path)
        with open(path, 'w') as fp:
            fp.write(f'{pid}\n')
    # log infos about application and execution mode
    log_info(f'running {INFO.name} v{INFO.version} on PID {pid}')
    return


# ----------------------------------------------------------------
# METHODS - getters / setters
# ----------------------------------------------------------------


def get_pid() -> int:
    return _PID


def set_pid(pid: int):
    global _PID
    _PID = pid
    return


def get_path_environment() -> str:
    return _PATH_ENV


def set_path_env(path: str):
    '''
    Set path to environment (client / server-side)
    '''
    global _PATH_ENV
    _PATH_ENV = path
    return


def get_path_session() -> str:
    return _PATH_SESSION


def get_path_in_session(path: str) -> str:
    return os.path.join(_PATH_SESSION, path)


def get_temp_path(filename: str | None = None) -> str:
    pid = get_pid()
    if filename is None:
        path = os.path.join('tmp', str(pid))
    else:
        path = os.path.join('tmp', str(pid), filename)
    return get_path_in_session(path)


def remove_temp_path() -> bool:
    path = get_temp_path()
    success = remove_dir_if_exists(path)
    return success


def set_path_session(path: str):
    '''
    Set path to session information (server-side).
    '''
    global _PATH_SESSION
    _PATH_SESSION = path
    return


def get_path_logging() -> str:
    return _PATH_LOGGING


def set_path_logging(path: str):
    '''
    Set path to directory where log files are to be stored.
    '''
    global _PATH_LOGGING
    _PATH_LOGGING = path
    return


def get_http_ip() -> str:
    path = _PATH_ENV
    return environment.get_http_ip(path)


def get_http_port() -> int:
    path = _PATH_ENV
    return environment.get_http_port(path)


# ----------------------------------------------------------------
# Load methods
# ----------------------------------------------------------------


def load_repo_info() -> RepoInfo:
    path = os.path.join(get_root_path(), 'pyproject.toml')
    with open(path, 'r', encoding=ENCODING.UTF8.value) as fp:
        config_repo = toml.load(fp)
        assets = config_repo.get('tool', {}).get('poetry', {})
        info = RepoInfo.model_validate(assets)
        return info


def get_version(info: RepoInfo) -> str:
    return info.version


def load_internal_config() -> AppConfig:
    path = _PATH_INTERNAL_CONFIG
    with open(path, 'rb') as fp:
        assets = yaml.load(fp, Loader=yaml.FullLoader)
        cfg: AppConfig = AppConfig.model_validate(assets)
        return cfg


def load_user_requests(path: str) -> list[RequestConfig]:
    with open(path, 'rb') as fp:
        assets = yaml.load(fp, Loader=yaml.FullLoader)
        cfg: RequestsConfig = RequestsConfig.model_validate(assets)
        return [req for req in cfg.requests if not req.ignore]


# ----------------------------------------------------------------
# LOAD RESOURCES
# ----------------------------------------------------------------

INFO = load_repo_info()
VERSION = get_version(INFO)

API_CONFIG = load_internal_config()
UNITS = API_CONFIG.settings.units
MATCHING = API_CONFIG.settings.matching
POLY = API_CONFIG.settings.polynomial
POINTS = API_CONFIG.settings.points
