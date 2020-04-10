#!/usr/bin/env python3
"""Defines the init for django-redis-sdk
"""


# from __future__ import


# __all__ = []
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from .cache_backend import (
    DjangoRedisSDKCache,
    DjangoRedisSDKShrededCache,
    DjangoRedisSDKDummyCache,
)
