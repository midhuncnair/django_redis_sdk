#!/usr/bin/env python3
"""Defines the base client for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'BaseClient',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import random

from collections import OrderedDict

from redis.connection import DefaultParser
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.module_loading import import_string
from django.core.exceptions import (
    ImproperlyConfigured
)

from .. import (
    connection,
)
from ..utils import (
    ConnectionException,
    custom_exception,
    EXCEPTIONS_TO_HANDLE,
    EXPIRED,
    NON_VOLATILE,
    get_client as gClient,
)


class BaseClient:
    """
    """
    def __init__(self, backend, servers, params):
        """
        """
        self._backend = backend
        self._servers = servers
        self._params = params

        self.make_key = self._backend.make_key
        self.validate_key = self._backend.validate_key

        self.clients = {}
        self._server_len = len(self._servers)

        self._options = self._params.get('OPTIONS', {})

        _db = self._params.get('db', self._options.get('DB', 0))
        try:
            self._db = int(_db)
        except(ValueError, TypeError):
            raise ImproperlyConfigured("db value must be an integer")

        self._password = self._params.get('password', self._options.get('PASSWORD', None))

        parser_class = self._options.get('PARSER_CLASS', None)
        if parser_class is None:
            self._parser_class = DefaultParser
        else:
            self._parser_class = import_string(parser_class)

        self._socket_timeout = self._options.get('SOCKET_TIMEOUT', None)
        if self._socket_timeout is not None:
            assert isinstance(
                self._socket_timeout, (int, float)
            ), "Socket timeout must be number"

        self._socket_connect_timeout = self._options.get('SOCKET_CONNECT_TIMEOUT', None)
        if self._socket_connect_timeout is not None:
            assert isinstance(
                self._socket_connect_timeout, (int, float)
            ), "Socket connect timeout must be number"

        self._options['cured_db'] = self._db
        self._options['cured_password'] = self._password
        self._options['cured_parser_class'] = self._parser_class
        self._options['cured_socket_timeout'] = self._socket_timeout
        self._options['cured_socket_connect_timeout'] = self._socket_connect_timeout

        self._serializer_class_path = self._options.get(
            'SERIALIZER_CLASS',
            'django_redis_sdk.serializers.PickleSerializer'
        )

        self._serializer_class = import_string(self._serializer_class_path)
        self._serializer = self._serializer_class(
            self._options,
            **self._options.get('SERIALIZER_CLASS_KWARGS', {})
        )

        self._compressor_class_path = self._options.get(
            'COMPRESSOR_CLASS',
            'django_redis_sdk.compressors.DummyCompressor'
        )
        self._compressor_class = import_string(self._compressor_class_path)
        self._compressor = self._compressor_class(
            self._options,
            **self._options.get('COMPRESSOR_CLASS_KWARGS', {})
        )

        self.connection_creator = connection.connection_factory(options=self._options)

    def get_client(self, write=True, tried_indices=None, return_index=False, **kwargs):
        """gets the client in a load balanced way.
        """
        if (
            write is True
            or self._server_len == 1
        ):
            index = 0  # write should be to primary

        elif tried_indices and len(tried_indices)< self._server_len:
            left_indices = [
                i for i in range(0, self._server_len)
                if i not in tried_indices
            ]

            if len(left_indices) > 1:
                # if more numbers left untried remove the write server.
                left_indices.remove(0)

            index = random.choice(left_indices)
        else:
            index = random.randint(1, self._server_len - 1)

        self.clients[index] = self.clients.get(
            index,
            self.connect(self._servers[index])
        )
        if return_index:
            return self.clients[index], index
        else:
            return self.clients[index]

    def connect(self, server):
        """Connects to the Redis server.
        """
        return self.connection_creator.connect(server)

    @gClient(write=False)
    def add(self, key, value, client=None, version=None, timeout=DEFAULT_TIMEOUT):
        """Adds the cache if key doesn't exist
        """
        return self.set(key, value, timeout, version=version, client=client, nx=True)

    @gClient(write=False)
    @custom_exception
    def get(self, key, client=None, default=None, version=None):
        """Gets the value from cache for given key.
        """
        key = self.make_key(key, version=version)
        value = client.get(key)

        if value is None:
            return default

        return self.deprocess(value)

    @custom_exception
    def set(self, key, value, version=None, client=None, timeout=DEFAULT_TIMEOUT, nx=False, xx=False):
        """
        nx if not exist
        xx if exist
        """
        key = self.make_key(key, version=version)
        value = self.process(value)

        if timeout is DEFAULT_TIMEOUT:
            timeout = self._backend.default_timeout

        current_client = client
        tried_indices = []
        while True:  # try until you exhaust all the servers
            try:
                if current_client is None:
                    current_client, index = self.get_client(
                        key=key,
                        write=True,
                        tried_indices=tried_indices,
                        return_index=True
                    )
                if timeout is not None:
                    if timeout <= 0:
                        # this pratically means delete
                        if nx:
                            # if nx: add if not exist-> if exist don't act, if not just add for 0 sec
                            # so we will just check if the key exists or not.
                            return not self.has_key(key, client=current_client, version=version)
                        else:
                            # this means set the key with negative timeout in all cases.
                            # pratically just to delete.
                            return self.delete(key, client=current_client, version=version)

                return bool(current_client.set(key, value, nx=nx, ex=timeout, xx=xx))

            except EXCEPTIONS_TO_HANDLE as err:
                if (
                    len(tried_indices) < self._server_len
                    and client is None
                ):
                    current_client = None
                    tried_indices.append(index)
                else:
                    raise type(err) from err

    @gClient(write=True)
    def touch(self, key, client=None, version=None, timeout=DEFAULT_TIMEOUT):
        """This will set new expiration for the key
        """
        return self.expire(key, timeout, client=client)

    @gClient(write=True)
    @custom_exception
    def delete(self, key, client=None, version=None):
        """Delete/Remove key from the cache.
        """
        key = self.make_key(key, version=version)
        return client.delete(key)

    @custom_exception
    def get_many(self, keys, client=None, version=None):
        """get values for multiple keys at once.
        """
        if client is None:
            client = self.get_client(write=False)

        if not keys:
            return {}

        ret_data = OrderedDict()

        versioned_keys_map = OrderedDict(
            (
                self.make_key(
                    key,
                    version=version
                ),
                key
            ) for key in keys
        )  #  OrderedDict((versioned_key, original_key), ...)

        values = client.mget(*versioned_keys_map)  # [versioned_key1, versioned_key2, ...]

        keys_to_values = zip(versioned_keys_map, values)
        """
            [(versioned_key1, value1), (versioned_key2, value2),  ...]
        """

        for k, v in keys_to_values:
            if v is not None:
                ret_data[
                    versioned_keys_map[k]  # gets original key for versioned_key
                ] = self.deprocess(v)

        return ret_data

    def get_or_set(self, key, default, client=None, version=None, timeout=DEFAULT_TIMEOUT):
        """Fetch a given key from the cache. If the key does not exist,
        add the key and set it to the default value. The default value can
        also be any callable. If timeout is given, use that timeout for the
        key; otherwise use the default cache timeout.

        Return the value of the key stored or retrieved.
        """
        key = self.make_key(key, version=version)
        val = self.get(key, version=version)

        if val is None:
            if callable(default):
                default = default()
            if default is not None:
                self.add(key, default, timeout=timeout, version=version)
                return self.get(key, default, version=version)
        return val

    @gClient(write=False)
    @custom_exception
    def has_key(self, key, client=None, version=None):
        """checks if the key exists.
        """
        key = self.make_key(key, version=version)

        return client.exists(key) == 1

    @gClient(write=True)
    @custom_exception
    def incr(self, key, client=None, delta=1, version=None):
        """Add delta to value in the cache. If the key does not exist, raise a
        ValueError exception.
        """
        key = self.make_key(key, version=version)
        value = self.get(key, version=version)

        if not client.exists(key):
            raise ValueError("Key '%s' not found" % key)

        value = client.incr(key, delta)

        return value

    def decr(self, key, client=None, delta=1, version=None):
        """Subtract delta from value in the cache. If the key does not exist, raise
        a ValueError exception.
        """
        return self.incr(key, -delta, version=version, client=client)

    @custom_exception
    def set_many(self, data, version=None, client=None, timeout=DEFAULT_TIMEOUT):
        """set multiple values to the cache at once
        """
        if client is None:
            client = self.get_client(write=True)

        pipeline = client.pipeline()
        for k, v in data.items():
            self.set(k, v, version=version, client=pipeline, timeout=timeout)
        pipeline.execute()

    @custom_exception
    def delete_many(self, keys, version=None, client=None):
        """Deletes multiple values from the cache at once
        """
        if client is None:
            client = self.get_client(write=True)

        if len(keys) <= 0:
            return

        keys = [
            self.make_key(i, version=version)
            for i in keys
        ]
        return client.delete(*keys)

    @custom_exception
    def clear(self, client=None):
        """ Clears/Flushes all cache key-values.
        """
        if client is None:
            client = self.get_client(write=True)

        client.flushdb()

    @gClient(write=True)
    def incr_version(self, key, client=None, delta=1, version=None):
        """Add delta to the cache version for the supplied key. Return the new
        version.
        """
        if version is None:
            version = self._backend.version

        value = self.get(key, version=version, client=client)
        if value is None:
            raise ValueError("Key '%s' not found" % key)

        self.set(key, value, version=version + delta)
        self.delete(key, version=version)

        return version + delta

    def decr_version(self, key, client=None, delta=1, version=None):
        """Subtract delta from the cache version for the supplied key. Return the
        new version.
        """
        return self.incr_version(key, delta=-delta, version=version, client=client)

    def close(self, **kwargs):
        """Close the cache connection
        """
        if self._options.get("REDIS_CLOSE_CONNECTION", False):
            for i in self.clients:
                for c in self.clients[i].connection_pool._available_connections:
                    c.disconnect()
                self.clients[i] = None

    def __contains__(self, key):
        """checks if the key exist in the cache
        version doesn't matter
        """
        return self.has_key(key)

    @gClient(write=False)
    @custom_exception
    def ttl(self, key, client=None, version=None):
        """Returns the ttl(time-to-live) of a key, if the key is non volitile.
        If key is a non volatile key; return None.
        Executes redis ttl command of specified key to find the ttl.
        """

        key = self.make_key(key, version=version)
        if not client.exists(key):
            return 0

        ttl = client.ttl(key)
        if ttl == NON_VOLATILE:
            return None
        elif ttl == EXPIRED:
            return 0
        else:
            return ttl

    @gClient(write=True)
    @custom_exception
    def lock(
        self,
        key,
        client=None,
        version=None,
        timeout=None,
        sleep=0.1,
        blocking_timeout=None
    ):
        """Returns the clients lock for a given key with provided params
        """

        key = self.make_key(key, version=version)

        return client.lock(
            key,
            timeout=timeout,
            sleep=sleep,
            blocking_timeout=blocking_timeout
        )

    @gClient(write=True)
    @custom_exception
    def persist(self, key, client=None, version=None):
        """Remove the timeout on given key.
        """

        key = self.make_key(key, version=version)

        if client.exists(key):
            return client.persist(key)

        return False

    @gClient(write=True)
    @custom_exception
    def expire(self, key, timeout, client=None, version=None):
        """
        """

        key = self.make_key(key, version=version)

        if client.exists(key):
            client.expire(key, timeout)

    def deprocess(self, processed):
        """
        Deprocess the given processed value.
        """
        try:
            value = int(processed)
        except (ValueError, TypeError):
            value = self._compressor.decompress(processed)
            value = self._serializer.deserialize(value)
        return value

    def process(self, unprocessed):
        """
        process the give unprocessed value.
        """
        if isinstance(unprocessed, int) and not isinstance(unprocessed, bool):
            return unprocessed

        value = self._serializer.serialize(unprocessed)
        return self._compressor.compress(value)
