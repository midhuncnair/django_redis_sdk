#!/usr/bin/env python3
"""Defines the DjangoRedisSDKShrededCacheClass for cache backends of django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'DjangoRedisSDKShrededCache',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from django.utils.module_loading import import_string

from .base import (
    BaseRedisSdk,
)


class DjangoRedisSDKShrededCache(BaseRedisSdk):
    """Shard support cache backend
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

        self._client_class_path = self._options.get(
            "CLIENT_CLASS",
            "django_redis_sdk.clients.ShardedClient"
        )
        self._client_class = import_string(self._client_class_path)
        self._client_object = None
