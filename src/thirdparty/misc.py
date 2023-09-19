#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from copy import copy
from itertools import product as itertools_product
from textwrap import dedent as textwrap_dedent
import datetime
import lorem
import pendulum

import re
from functools import wraps
from typing import Callable
from typing import TypeVar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MODIFICATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def strip_around(
    text: str,
    first: bool,
    last: bool,
    all: bool = True,
):
    '''
    Strips all initial/final 'empty' lines.
    '''
    lines = re.split(pattern=r'\n', string=text)
    if all:
        if first:
            while len(lines) > 0 and lines[0].strip() == '':
                lines = lines[1:]
        if last:
            while len(lines) > 0 and lines[-1].strip() == '':
                lines = lines[:-1]
    else:
        if first:
            lines = lines[1:]
        if last:
            lines = lines[:-1]
    text = '\n'.join(lines)
    return text


def dec_prestrip(first: bool = True, last: bool = True, all: bool = False):
    '''
    Returns a decorator that modifies string -> string methods
    '''
    T = TypeVar('T')

    def dec(method: Callable[[str], T]) -> Callable[[str], T]:
        '''
        Performs method but first strips all initial/final 'empty' lines.
        '''

        @wraps(method)
        def wrapped_method(text: str) -> T:
            text = strip_around(text, first=first, last=last, all=all)
            return method(text)

        return wrapped_method

    return dec


@dec_prestrip(all=False)
def dedent(text: str) -> str:
    '''
    Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalised to a newline character.
    '''
    return textwrap_dedent(text)


@dec_prestrip(all=True)
def dedent_full(text: str) -> str:
    '''
    Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalised to a newline character.

    NOTE: this method completely strips all pre/post empty lines
    (= lines containing at most only white spaces).
    '''
    return textwrap_dedent(text)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'copy',
    'datetime',
    'dedent',
    'dedent_full',
    'itertools_product',
    'lorem',
    'lorem',
    'pendulum',
    're',
    'strip_around',
    'timedelta',
]
