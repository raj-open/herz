#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from copy import copy
from copy import deepcopy
from dataclasses import MISSING
from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from functools import reduce
from functools import wraps
from itertools import chain as itertools_chain
from itertools import product as itertools_product
from operator import itemgetter

# cf. https://github.com/mplanchard/safetywrap
from typing import Callable
from typing import Optional
from typing import ParamSpec
from typing import TypeVar

from lazy_load import lazy
from pydantic import BaseModel

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------

PARAMS = ParamSpec("PARAMS")
RETURN = TypeVar("RETURN")
MODEL = TypeVar("MODEL", bound=BaseModel)


def echo_function(message: Optional[str] = None):
    """
    Decorates method with an echo method.
    """

    def dec(f: Callable[PARAMS, RETURN]) -> Callable[PARAMS, RETURN]:
        # prepare the message
        message_ = f"fct:{f.__name__}" + ("" if message is None else f"    {message}")

        # modify function
        @wraps(f)
        def f_(*args: PARAMS.args, **kwargs: PARAMS.kwargs) -> RETURN:
            print(message_)
            output = f(*args, **kwargs)
            return output

        return f_

    return dec


def make_lazy(method: Callable[PARAMS, RETURN]) -> Callable[PARAMS, RETURN]:
    """
    Decorates a method and makes it return a lazy-load output.
    """

    @wraps(method)
    def wrapped_method(*args: PARAMS.args, **kwargs: PARAMS.kwargs) -> RETURN:
        return lazy(partial(method), *args, **kwargs)

    return wrapped_method


def value_of_model(m: MODEL):
    return m.root


def compute_once(method: Callable[PARAMS, RETURN]) -> Callable[PARAMS, RETURN]:
    """
    Decorates a possibly expensive method to ensure that it only computes once
    and thereafter simply returns an internally stored value.

    If for some reason the value is destroyed, then recomputes this.
    """
    _value = None
    _first = True

    @wraps(method)
    def wrapped_method(*args: PARAMS.args, **kwargs: PARAMS.kwargs) -> RETURN:
        nonlocal _value
        nonlocal _first
        if _first or _value is None:
            _value = method(*args, **kwargs)
        _first = False
        return _value

    return wrapped_method


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "MISSING",
    "Field",
    "asdict",
    "compute_once",
    "copy",
    "dataclass",
    "deepcopy",
    "echo_function",
    "field",
    "itemgetter",
    "itertools_chain",
    "itertools_product",
    "lazy",
    "make_lazy",
    "partial",
    "reduce",
    "value_of_model",
    "wraps",
]
