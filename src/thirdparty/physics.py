#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

import pint

from typing import Optional

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------

_ureg = None


def convert_units(unitFrom: str, unitTo: str) -> float:
    global _ureg
    # NOTE: register once, otherwise costs too much time!
    _ureg = _ureg or pint.UnitRegistry()
    cv = _ureg.Quantity(1, unitFrom).to(unitTo).magnitude
    return cv


def print_unit(text: str, ascii: bool = True) -> Optional[str]:
    global _ureg
    # NOTE: register once, otherwise costs too much time!
    _ureg = _ureg or pint.UnitRegistry()
    try:
        u = _ureg.Unit(text)
        return f'{u:~C}' if ascii else f'{u:~P}'
    except:
        return None


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'convert_units',
    'print_unit',
    'pint',
]
