#!/usr/bin/env python3
"""Defines the compressors init for django-redis-sdk backends
"""


# from __future__ import


# __all__ = []
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]

from .base_compressor import (
    BaseCompressor,
    DummyCompressor,
)
from .zlib_compressor import (
    ZlibCompressor,
)
