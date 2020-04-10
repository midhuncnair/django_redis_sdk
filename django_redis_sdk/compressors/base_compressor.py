#!/usr/bin/env python3
"""Defines the base compressor for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'BaseCompressor',
    'DummyCompressor',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


class BaseCompressor:
    """Defines the Base Compressor
    """

    def __init__(self, options, **kwargs):
        """Initializes the Compressor
        """
        self._options = options

    def compress(self, value):
        """compresss the value
        needs to be implemented in inheriting class
        """
        raise NotImplementedError("BaseClass")

    def decompress(self, value):
        """Decompresss the value
        needs to be implemented in inheriting class
        """
        raise NotImplementedError("BaseClass")

    class Meta:
        abstract = True


class DummyCompressor(BaseCompressor):
    """Defines the Dummy Compressor
    can be used if no serialization is needed.
    """

    def compress(self, value):
        return value

    def decompress(self, value):
        return value
