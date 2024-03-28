#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from src.thirdparty.config import *
from src.thirdparty.types import *
from src.thirdparty.misc import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'YamlImports',
    'YamlLongString',
    'read_yaml',
    'write_yaml',
    'get_dumper',
    'register_enum_for_yaml_dumping',
];

# ----------------------------------------------------------------
# LOCAL CONSTANTS
# ----------------------------------------------------------------

_yaml_constructors_registered = False;
_yaml_dumpers_registered = False;
_yaml_registered_types: list[str] = [];

# ----------------------------------------------------------------
# CLASS-WRAPPERS
# ----------------------------------------------------------------

class YamlLongString(str):
    value: str;

    def __init__(self, x: Any):
        self.value = str(x);
        return;

    def __str__(self) -> str:
        return self.value;

class YamlImports(str):
    value: str;

    def __init__(self, x: str):
        self.value = x;
        return;

    def __str__(self) -> str:
        return self.value;

# ----------------------------------------------------------------
# METHODS
# ----------------------------------------------------------------

def read_yaml(path: str):
    register_yaml_constructors();
    with open(path, 'rb') as fp:
        return yaml.load(fp, yaml.FullLoader);

def write_yaml(
    path: str,
    obj: dict,
    sort_keys: bool = False,
    n: int = 0,
):
    register_yaml_dumpers();
    with open(path, 'w') as fp:
        yaml.dump(
            obj,
            stream=fp,
            sort_keys=sort_keys,
            indent=2,
            encoding='utf-8',
            allow_unicode=True,
            Dumper=get_dumper(n),
        );
    return;

# ----------------------------------------------------------------
# REGISTER CONSTRUCTORS
# ----------------------------------------------------------------

def register_yaml_constructors():
    global _yaml_constructors_registered;

    if _yaml_constructors_registered:
        return;

    def include_constructor(loader: yaml.Loader, node: yaml.Node):
        try:
            value = loader.construct_yaml_str(node);
            assert isinstance(value, str);
            m = re.match(pattern=r'^(.*)\/#\/?(.*)$', string=value)
            path = m.group(1) if m else value
            keys_as_str = m.group(2) if m else ''
            obj = read_yaml(path)
            keys = keys_as_str.split('/')
            for key in keys:
                if key == '':
                    continue
                obj = obj.get(key, dict());
            return obj
        except:
            return None

    def not_constructor(loader: yaml.Loader, node: yaml.Node) -> bool:
        try:
            value = loader.construct_yaml_bool(node);
            return not value;
        except:
            return None;

    def join_constructor(loader: yaml.Loader, node: yaml.Node):
        try:
            values = loader.construct_sequence(node, deep=True);
            sep, parts = str(values[0]), [str(_) for _ in values[1]];
            return sep.join(parts);
        except:
            return '';

    def tuple_constructor(loader: yaml.Loader, node: yaml.Node):
        try:
            value = loader.construct_sequence(node, deep=True);
            return tuple(value);
        except:
            return None;

    yaml.add_constructor(tag=u'!include', constructor=include_constructor);
    yaml.add_constructor(tag=u'!not', constructor=not_constructor);
    yaml.add_constructor(tag=u'!join', constructor=join_constructor);
    yaml.add_constructor(tag=u'!tuple', constructor=tuple_constructor);

    _yaml_constructors_registered = True;
    return;

# ----------------------------------------------------------------
# REGISTER DUMPERS
# ----------------------------------------------------------------

def register_enum_for_yaml_dumping(tt: type):
    global _yaml_registered_types;
    if tt.__name__ in _yaml_registered_types:
        return;

    _yaml_registered_types.append(tt.__name__);

    def _register(dumper: yaml.Dumper, data: tt):
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data);
    yaml.add_representer(tt, _register);
    yaml.representer.SafeRepresenter.add_representer(tt, _register);
    return;

def register_yaml_dumpers():
    global _yaml_dumpers_registered;

    if _yaml_dumpers_registered:
        return;

    yaml.add_representer(YamlLongString, _repr_long_strings);
    yaml.representer.SafeRepresenter.add_representer(YamlLongString, _repr_long_strings);
    yaml.add_representer(YamlImports, _repr_imports);
    yaml.representer.SafeRepresenter.add_representer(YamlImports, _repr_imports);
    _yaml_dumpers_registered = True;
    return;

def _repr_long_strings(
    dumper: yaml.Dumper,
    data: YamlLongString,
):
    return dumper.represent_scalar(
        u'tag:yaml.org,2002:str',
        data,
        style='|',
    );

def _repr_imports(
    dumper: yaml.Dumper,
    data: YamlImports,
):
    return dumper.represent_scalar(u'!include', data, style='"');

# ----------------------------------------------------------------
# AUXILIARY METHODS
# ----------------------------------------------------------------


def get_dumper(n: int = 0) -> yaml.Dumper:
    class DumperExtraLineSpacing(yaml.SafeDumper):
        def write_line_break(self, data: Any = None):
            super().write_line_break(data);
            level = len(self.indents);
            if level <= n:
                super().write_line_break();
            return;

        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False);

    return DumperExtraLineSpacing;