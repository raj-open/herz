#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE:
# Reads in pyproject.toml and generates the requirements.txt file.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys

os.chdir(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.getcwd())

from pathlib import Path
import re
import toml
from typing import Any
from typing import Optional

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PATHS_DEPENDENCIES = [
    'project.dependencies',
    'project.optional-dependencies.test',
    'project.optional-dependencies.dev',
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN METHOD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def enter(path_toml: str, path_req: str, *_):
    with open(path_toml, 'r') as fp:
        obj = toml.load(fp)
        project_name = get_package_name(obj)
        requirements = get_package_dependencies(obj, exclude=[project_name, 'python'])
    path = Path(path_req)
    # os.remove(path_req);
    path.touch()
    with open(path_req, 'w') as fp:
        for cond in requirements:
            fp.write(cond)
            fp.write('\n')
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_package_name(obj: dict) -> Optional[str]:
    name = obj.get('project', {}).get('name', None)
    if not isinstance(name, str):
        return None
    name = name.strip()
    if name == '':
        return None
    return name


def get_package_dependencies(
    obj: Any,
    path: str = '',
    name: Optional[str] = None,
    exclude: list[str] = [],
) -> dict:
    req = []
    match (
        path in PATHS_DEPENDENCIES,
        name,
        name in exclude,
        isinstance(obj, dict),
        isinstance(obj, str),
    ):
        case _, None, _, False, _:
            pass
        case False, None, _, True, _:
            for key, value in obj.items():
                req += get_package_dependencies(
                    value, path=key if path == '' else f'{path}.{key}', exclude=exclude
                )
        case True, None, _, True, _:
            for key, value in obj.items():
                req += get_package_dependencies(
                    value, path=path, name=key, exclude=exclude
                )
        case _, _, True, _, _:
            pass
        case _, _, _, _, True:
            pkg = package_version(name=name, version=obj)
            req.append(pkg)
        case _, _, _, True, _:
            pkg = name
            if 'extras' in obj:
                extras = obj['extras']
                if not isinstance(extras, list):
                    extras = [extras]
                extras = ', '.join(extras)
                pkg = f'{name}[{extras}]'
            if 'version' in obj:
                pkg = package_version(name=pkg, version=obj['version'])
            if 'url' in obj:
                url: str = obj['url']
                pkg = f'{pkg} -f {url}'
            req.append(pkg)
    return req


def package_version(name: str, version: str) -> str:
    if version.startswith('^'):
        version = version[1:]
        return f'{name}>={version}'
    elif re.match(pattern=r'\>|\<', string=version):
        return f'{name}{version}'
    else:
        return f'{name}=={version}'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXECUTION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    args = sys.argv[1:]
    enter(*args)
