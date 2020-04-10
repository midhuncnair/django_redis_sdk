#!/usr/bin/env python3
"""Defines the common utils for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'handle_exception',
    'get_servers',
    'custom_exception',
    'EXCEPTIONS_TO_HANDLE',
    'EXPIRED',
    'NON_VOLATILE',
    'get_client',
    'sanitize_params',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import logging
import socket

from functools import (
    wraps
)
from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from django.core.exceptions import (
    ImproperlyConfigured
)

from .exceptions import (
    ConnectionException,
)


EXCEPTIONS_TO_HANDLE = (socket.timeout, TimeoutError, ConnectionError, ResponseError)
EXPIRED = -2
NON_VOLATILE = -1
VALID_OPTIONS_DEFAULTS = {
    'DB': 0,
    'PASSWORD': None,
    'CLIENT_CLASS': None,
    'PARSER_CLASS': 'redis.connection.DefaultParser',
    'CONNECTION_POOL_CLASS': 'redis.connection.ConnectionPool',
    'CONNECTION_POOL_CLASS_KWARGS': {},
    'SERIALIZER_CLASS': 'django_redis_sdk.serializers.PickleSerializer',
    'SERIALIZER_CLASS_KWARGS': {},
    'PICKLE_VERSION': -1,
    'COMPRESSOR_CLASS': 'django_redis_sdk.compressors.DummyCompressor',
    'COMPRESSOR_CLASS_KWARGS': {},
    'COMPRESS_LEVEL': 5,
    'REDIS_CLIENT_CLASS': 'redis.client.Redis',
    'REDIS_CLIENT_KWARGS': {},
    'SOCKET_CONNECT_TIMEOUT': None,
    'SOCKET_TIMEOUT': None,
    'HANDLE_EXCEPTIONS': False,
    'LOG_EXCEPTIONS': False,
    'LOGGER_NAME': None,
}

def custom_exception(func):
    """This will convert the known set of exceptions
    that are to be handled to the custom exception
    """
    @wraps(func)
    def decorated_func(*args, **kwargs):
        """
        """
        try:
            return func(*args, **kwargs)
        except EXCEPTIONS_TO_HANDLE as err:
            raise ConnectionException(
                client=kwargs.get('client', None),
                from_error=err
            )
    return decorated_func


def handle_exception(default_value=None):
    """ This function is used to handle the exceptions
    first defines the default value to return then returns if
    handling.
    """

    def partial_func(func):
        """
        """
        @wraps(func)
        def decorated_func(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ConnectionException as err:
                if self._handle_exception:
                    if self._log_exception:
                        logging.getLogger(self._logger).error(
                            str(err)
                        )

                    return default_value

                raise ConnectionException(err.client, from_error=err.from_error) from err

        return decorated_func

    return partial_func


def get_servers(in_servers):
    """validates and returns the servers
    """
    if isinstance(in_servers, str):
        servers = in_servers.split(',')

    elif hasattr(in_servers, '__iter__'):
        servers = in_servers

    else:
        raise ImproperlyConfigured(
            'Server/Location: Definition Missing/ImproperlyConfigured'
            + ' - "server" should be a string or iterable.'
        )

    return servers


def get_client(method='get_client', write=False):

    def partial_func(func):

        @wraps(func)
        def decorated_func(self, key, *args, **kwargs):
            version = kwargs.get('version', None)
            n_key = self.make_key(key, version=version)
            self_get_client = getattr(self, method)
            client = self_get_client(key=n_key, write=write)
            kwargs['client'] = client
            return func(self, key, *args, **kwargs)

        return decorated_func

    return partial_func


def sanitize_params(in_params):
    """
    """
    in_options = in_params.get('OPTIONS') or {}
    out_params = {}
    out_options = {}
    for k, v in VALID_OPTIONS_DEFAULTS.items():
        value = in_options.get(k) or v
        if value is not None:
            out_options[k] = value
    for k, v in in_options.items():
        if k not in out_options:
            out_options[k] = v
    out_params['OPTIONS'] = out_options

    for k, v in in_params.items():
        if k not in out_params:
            out_params[k] = v
    return out_params
