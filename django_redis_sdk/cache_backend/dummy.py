#!/usr/bin/env python3
"""Defines the DummyCacheClass for cache backends of django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'DjangoRedisSDKDummyCache',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from django.core.cache.backends.dummy import DummyCache


class DjangoRedisSDKDummyCache(DummyCache):
    """
    """

    def ttl(self, key):
        return 0

    def get_or_set(self, key, default, timeout=None):
        if callable(default):
            return default()

        return default

    def persist(self, key):
        return True

    def expire(self, key, timeout):
        return True
