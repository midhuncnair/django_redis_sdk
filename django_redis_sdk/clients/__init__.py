#!/usr/bin/env python3
"""Defines the init for cache clients of django-redis-sdk backends
"""


# from __future__ import


# __all__ = []
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from .base_client import (
    BaseClient,
)

from .shard_client import (
    ShardedClient,
)
