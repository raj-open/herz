#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import Namespace
from argparse import RawTextHelpFormatter

# for modifications, not export
from enum import Enum
from io import BytesIO

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


# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "ENCODING",
    "ArgumentError",
    "ArgumentParser",
    "BytesIO",
    "BytesIOStream",
    "Namespace",
    "RawTextHelpFormatter",
]
