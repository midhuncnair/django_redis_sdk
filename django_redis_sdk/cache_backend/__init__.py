#!/usr/bin/env python3
"""Defines the init for cache backends of django-redis-sdk backends
"""


# from __future__ import


# __all__ = []
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from .base import (
    BaseRedisSdk,
)
from .single import (
    DjangoRedisSDKCache,
)
from .multiple import (
    DjangoRedisSDKShrededCache,
)
from .dummy import (
    DjangoRedisSDKDummyCache
)
