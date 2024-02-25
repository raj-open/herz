#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from pydantic import BaseModel
from copy import copy
from copy import deepcopy
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import Field
from dataclasses import MISSING
from functools import partial
from functools import reduce
from functools import wraps
from itertools import chain as itertools_chain
from itertools import product as itertools_product
from lazy_load import lazy
from operator import itemgetter

# cf. https://github.com/mplanchard/safetywrap
from typing import Callable
from typing import Optional
from typing import ParamSpec
from typing import TypeVar

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------

KWARGS = ParamSpec('KWARGS')
RETURN = TypeVar('RETURN')
MODEL = TypeVar('MODEL', bound=BaseModel)


def echo_function(message: Optional[str] = None):
    '''
    Decorates method with an echo method.
    '''

    def dec(f: Callable[KWARGS, RETURN]) -> Callable[KWARGS, RETURN]:
        # prepare the message
        message_ = f'fct:{f.__name__}' + ('' if message is None else f'    {message}')

        # modify function
        @wraps(f)
        def f_(*args, **kwargs) -> RETURN:
            print(message_)
            output = f(*args, **kwargs)
            return output

        return f_

    return dec


def make_lazy(method: Callable[KWARGS, RETURN]) -> Callable[KWARGS, RETURN]:
    '''
    Decorates a method and makes it return a lazy-load output.
    '''

    @wraps(method)
    def wrapped_method(**kwargs) -> RETURN:
        return lazy(partial(method), **kwargs)

    return wrapped_method


def value_of_model(m: MODEL):
    return m.root


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'Field',
    'MISSING',
    'asdict',
    'copy',
    'deepcopy',
    'dataclass',
    'echo_function',
    'field',
    'itemgetter',
    'itertools_chain',
    'itertools_product',
    'lazy',
    'make_lazy',
    'partial',
    'reduce',
    'value_of_model',
    'wraps',
]
