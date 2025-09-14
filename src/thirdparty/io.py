#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from enum import Enum
from io import BytesIO

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "ENCODING",
    "BytesIO",
    "BytesIOStream",
]

# ----------------------------------------------------------------
# MODIFICATIONS
# ----------------------------------------------------------------


class ENCODING(Enum):
    ASCII = "ascii"
    UTF8 = "utf-8"
    UNICODE = "unicode_escape"


class BytesIOStream:
    """
    Provides context manager for a bytes stream.
    """

    _contents: bytes

    def __init__(self, contents: bytes):
        self._contents = contents

    def __enter__(self):
        """
        Context manager for BytesIO that deals with seeking.
        """
        fp = BytesIO(self._contents).__enter__()
        fp.seek(0)
        return fp

    def __exit__(self, exc_type, exc_val, exc_tb):
        return
