#!/usr/bin/env python3
"""Defines the base class for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'BaseRedisSdk',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging

from django.core.cache.backends.base import (
    BaseCache,
    InvalidCacheBackendError,
    DEFAULT_TIMEOUT,
)
from django.utils.module_loading import import_string
from django.conf import settings

from ..utils import (
    handle_exception,
    sanitize_params,
    get_servers,
)


class BaseRedisSdk(BaseCache):
    """This is an **abstract** class which the other backend inherits from.
    """

    def __init__(self, servers, params):
        """Initializes the cache backend base
        """
        super().__init__(params)
        self._raw_servers = servers
        self._servers = get_servers(servers)

        self._raw_params = params
        self._params = sanitize_params(params)

        self._options = params.get("OPTIONS", {})
        self._client_object = None

        self._handle_exception = self._options.get("HANDLE_EXCEPTIONS", False)
        self._log_exception = self._options.get("LOG_EXCEPTIONS", False)
        self._logger = self._options.get("LOGGER_NAME", __name__)

    @property
    def client(self):
        """get client as needed
        """
        if self._client_object is None:
            self._client_object = self._client_class(self, self._servers, self._params)

        return self._client_object

    def __getattr__(self, attr):
        return getattr(self.client, attr)

    # cache api django defaults
    @handle_exception()
    def add(self, *args, **kwargs):
        """
        """
        return self.client.add(*args, **kwargs)

    @handle_exception()
    def get(self, *args, **kwargs):
        """
        """
        return self.client.get(*args, **kwargs)

    @handle_exception()
    def set(self, *args, **kwargs):
        """
        """
        return self.client.set(*args, **kwargs)

    @handle_exception()
    def touch(self, *args, **kwargs):
        """
        """
        return self.client.touch(*args, **kwargs)

    @handle_exception()
    def delete(self, *args, **kwargs):
        """
        """
        return self.client.delete(*args, **kwargs)

    @handle_exception(default_value={})
    def get_many(self, *args, **kwargs):
        """
        """
        return self.client.get_many(*args, **kwargs)

    @handle_exception()
    def get_or_set(self, *args, **kwargs):
        """
        """
        return self.client.get_or_set(*args, **kwargs)

    @handle_exception()
    def has_key(self, *args, **kwargs):
        """
        """
        return self.client.has_key(*args, **kwargs)

    @handle_exception()
    def incr(self, *args, **kwargs):
        """
        """
        return self.client.incr(*args, **kwargs)

    @handle_exception()
    def decr(self, *args, **kwargs):
        """
        """
        return self.client.decr(*args, **kwargs)

    @handle_exception()
    def set_many(self, *args, **kwargs):
        """
        """
        return self.client.set_many(*args, **kwargs)

    @handle_exception()
    def delete_many(self, *args, **kwargs):
        """
        """
        return self.client.delete_many(*args, **kwargs)

    @handle_exception()
    def clear(self, *args, **kwargs):
        """
        """
        return self.client.clear(*args, **kwargs)

    @handle_exception()
    def validate_key(self, *args, **kwargs):
        """
        """
        return self.client.validate_key(*args, **kwargs)

    @handle_exception()
    def incr_version(self, *args, **kwargs):
        """
        """
        return self.client.incr_version(*args, **kwargs)

    @handle_exception()
    def decr_version(self, *args, **kwargs):
        """
        """
        return self.client.decr_version(*args, **kwargs)

    @handle_exception()
    def close(self, *args, **kwargs):
        """
        """
        return self.client.close(*args, **kwargs)

    @handle_exception()
    def __contains__(self, *args, **kwargs):
        """
        """
        return self.client.__contains__(*args, **kwargs)

    # cache api extra functions
    @handle_exception()
    def ttl(self, *args, **kwargs):
        """
        """
        return self.client.ttl(*args, **kwargs)

    @handle_exception()
    def lock(self, *args, **kwargs):
        """
        """
        return self.client.lock(*args, **kwargs)

    @handle_exception()
    def persist(self, *args, **kwargs):
        """
        """
        return self.client.persist(*args, **kwargs)

    @handle_exception()
    def expire(self, *args, **kwargs):
        """
        """
        return self.client.expire(*args, **kwargs)

    class Meta:
        abstract = True
