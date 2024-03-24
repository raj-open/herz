#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from .resolve import *
from .merge import *

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    'compute_overlaps',
    'merge_intervals',
    'resolve_interval',
    'resolve_intervals',
]
