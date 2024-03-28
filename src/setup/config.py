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
from ..models.internal import *
from ..models.user import *
from .register import *

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

pid = Property[int]()
path_env = Property[str]()
path_logging = Property[str]()
path_session = Property[str]()
path_app_config = Property[str]()
http_ip = Property[str](lambda: environment.get_http_ip(path_env()))
http_port = Property[int](lambda: environment.get_http_port(path_env()))
path_app_config.set(os.path.join(get_source_path(), 'setup', 'config.yaml'))


# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------


def initialise_logging(
    name: str,
    debug: bool = False,
):
    '''
    Initialise logging.
    '''
    level = LOG_LEVELS.DEBUG if debug else LOG_LEVELS.INFO
    path = path_logging()
    configure_logging(name=name, level=level.name, path=path)
    return


def initialise_application(
    name: str,
    log_pid: str | None = None,
    debug: bool = False,
):
    '''
    Initialises cli execution of application
    '''
    # initialise logging
    initialise_logging(name=name, debug=debug)
    # store pid as single value
    path = log_pid or ''
    if path != '':
        path = get_path_in_session(path)
        create_file_if_not_exists(path)
        with open(path, 'w') as fp:
            fp.write(f'{pid()}\n')
    # log infos about application and execution mode
    log_info(f'running {INFO.name} v{INFO.version} on PID {pid()}')
    return


# ----------------------------------------------------------------
# QUERIES
# ----------------------------------------------------------------


def get_path_in_session(path: str) -> str:
    return os.path.join(path_session(), path)


def get_temp_path(filename: str | None = None) -> str:
    if filename is None:
        path = os.path.join('tmp', str(pid()))
    else:
        path = os.path.join('tmp', str(pid()), filename)
    return get_path_in_session(path)


def remove_temp_path() -> bool:
    path = get_temp_path()
    success = remove_dir_if_exists(path)
    return success


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
    assets = read_yaml(path=path_app_config())
    return AppConfig.model_validate(assets)


def load_user_requests(path: str) -> list[RequestConfig]:
    assets = read_yaml(path=path)
    cfg = RequestsConfig.model_validate(assets)
    return [req for req in cfg.requests if not req.ignore]


# ----------------------------------------------------------------
# LOAD RESOURCES
# ----------------------------------------------------------------

INFO = load_repo_info()
VERSION = get_version(INFO)

API_CONFIG = load_internal_config()
UNITS = API_CONFIG.settings.units
MATCHING = API_CONFIG.settings.matching
TRIG = API_CONFIG.settings.trigonometric
EXP = API_CONFIG.settings.exponential
POLY = API_CONFIG.settings.polynomial
POINTS = API_CONFIG.settings.points
