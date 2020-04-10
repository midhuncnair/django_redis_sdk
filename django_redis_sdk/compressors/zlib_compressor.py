#!/usr/bin/env python3
"""Defines the zlib compressor for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'ZlibCompressor',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import zlib
from django.core.exceptions import ImproperlyConfigured

from .base_compressor import (
    BaseCompressor
)


class ZlibCompressor(BaseCompressor):
    """Defines the Zlib compressor
    """

    def __init__(self, options, **kwargs):
        """Initializes the Compressor
        """
        super().__init__(options, **kwargs)

        _level = self._options.get('COMPRESS_LEVEL', None)
        _level = kwargs.get('COMPRESS_LEVEL', None) or _level or 5

        try:
            self._level = int(_level)
        except (ValueError, TypeError):
            raise ImproperlyConfigured(
                "COMPRESS_LEVEL: expected integer got '%s'" % type(_level)
            )

        if (self._level < 1 or self._level > 9):
            raise ImproperlyConfigured(
                "COMPRESS_LEVEL: expected value between [1 - 9] both inclusive"
            )

    @property
    def level(self):
        """level property
        """
        return self._level


    def compress(self, value):
        """Compresses the value
        """
        return zlib.compress(value, self._level)

    def decompress(self, value):
        """Decompresses the value
        """
        return zlib.decompress(value)
