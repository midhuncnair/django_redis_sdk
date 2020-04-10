#!/usr/bin/env python3
"""Defines the connection for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'ConnectionPool',
    'connection_factory',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from copy import deepcopy

from django.utils.module_loading import import_string
from six.moves.urllib.parse import parse_qs, urlparse
from redis.connection import (
    SSLConnection,
    UnixDomainSocketConnection,
    Connection,
)
from django.core.exceptions import (
    ImproperlyConfigured
)


class ConnectionPool:
    """This creates and stores the connection pool for each django instance
    as opposed to each request so that the connection can be reused.
    """
    _connection_pool = {}  # global space singleton

    def __init__(self, options):
        """Initializes the connection pool
        """
        self._options = options
        self._connection_pool_class_path = self._options.get(
            "CONNECTION_POOL_CLASS",
            "redis.connection.ConnectionPool"
        )
        self._connection_pool_cls = import_string(self._connection_pool_class_path)
        self._connection_pool_cls_kwargs = self._options.get("CONNECTION_POOL_CLASS_KWARGS", {})

        self._redis_client_cls_path = self._options.get(
            "REDIS_CLIENT_CLASS",
            "redis.client.Redis"
        )
        self._redis_client_cls = import_string(self._redis_client_cls_path)
        self._redis_client_cls_kwargs = self._options.get("REDIS_CLIENT_KWARGS", {})

    def get_connection_default_params(self, server):
        """get connection's default params
        """
        params = {
            "url": server,
            "parser_class": self._options['cured_parser_class'],
            "db": self._options['cured_db'],
            "password": self._options['cured_password'],
            "socket_timeout": self._options['cured_socket_timeout'],
            "socket_connect_timeout": self._options['cured_socket_connect_timeout'],
        }

        return params

    def parse_server_params(self, server, db=None, **kwargs):
        """
        Return a connection pool configured from the given URL.

        For example::

            redis://[:password]@localhost:6379/0
            rediss://[:password]@localhost:6379/0
            unix://[:password]@/path/to/socket.sock?db=0

        Three URL schemes are supported:
            redis:// creates a normal TCP socket connection
            rediss:// creates a SSL wrapped TCP socket connection
            unix:// creates a Unix Domain Socket connection

        There are several ways to specify a database number. The parse function
        will return the first specified option:
            1. A ``db`` querystring option, e.g. redis://localhost?db=0
            2. If using the redis:// scheme, the path argument of the url, e.g.
            redis://localhost/0
            3. The ``db`` argument to this function.

        If none of these options are specified, db=0 is used.

        Any additional querystring arguments and keyword arguments will be
        passed along to the ConnectionPool class's initializer. In the case
        of conflicting arguments, querystring arguments always win.

        NOTE: taken from `redis.ConnectionPool.from_url` in redis-py
        """
        kwargs['path'] = ''
        if '://' in server:
            url = server
            url = urlparse(url)
            qs = url.query

            url_options = {}

            for k, v in parse_qs(qs).items():
                if v and len(v) > 0:
                    url_options[k] = v[0]

            if url.scheme == 'unix':
                url_options.update(
                    {
                        'password': url.password,
                        'path': url.path,
                        'connection_class': UnixDomainSocketConnection,
                    }
                )
            else:
                url_options.update(
                    {
                        'host': url.hostname,
                        'port': int(url.port or 6379),
                        'password': url.password,
                        'connection_class': Connection,
                    }
                )

                # If there's a path argument, use it as the db argument if a
                # querystring value wasn't specified
                if 'db' not in url_options and url.path:
                    try:
                        url_options['db'] = int(url.path.replace('/', ''))
                    except (AttributeError, ValueError):
                        pass

                if url.scheme == 'rediss':
                    url_options['connection_class'] = SSLConnection

            # last shot at the db value
            url_options['db'] = int(url_options.get('db', db or 0))

            # update the arguments from the URL values
            kwargs.update(url_options)

        else:
            path = None
            if ':' in server:
                host, port = server.rsplit(':', 1)
                connection_class = Connection
                try:
                    port = int(port)
                    url = "redis://%s:%s" % (host, port)
                except (ValueError, TypeError):
                    raise ImproperlyConfigured(
                        "%s from %s must be an integer" %(
                            repr(port),
                            server
                        )
                    )
            else:
                host, port = None, None
                path = server
                connection_class = UnixDomainSocketConnection
                url = "unix://%s" % server

            kwargs.update(
                host=host,
                port=port,
                path=path,
                db=db,
                connection_class = connection_class,
                url=url,
            )

        return kwargs

    def connect(self, server):
        """connect to the server and returns the connection
        """
        params = self.get_connection_default_params(server)
        params = self.parse_server_params(server, **params)
        connection = self.get_connection(params)
        return connection

    def get_connection(self, params):
        """Gets or create new connection pool and then
        makes new redis client connection and returns
        """
        pool_key = params["url"]
        if pool_key not in self._connection_pool:
            self._connection_pool[pool_key] = self.get_connection_pool(params)

        return self._redis_client_cls(
            connection_pool=self._connection_pool[pool_key],
            **self._redis_client_cls_kwargs
        )

    def get_connection_pool(self, params):
        """create a connection pool with the given params
        """
        pool_params = deepcopy(params)
        pool_params.update(self._connection_pool_cls_kwargs)

        if 'path' in pool_params:
            path = pool_params.pop('path')
        else:
            path = None

        if (
            'connection_class' in pool_params
            and issubclass(pool_params['connection_class'], UnixDomainSocketConnection)
        ):
            pool_params['path'] = path

        connection_pool = self._connection_pool_cls.from_url(**pool_params)

        if connection_pool.connection_kwargs.get("password", None) is None:
            connection_pool.connection_kwargs["password"] = params.get("password", None)
            connection_pool.reset()

        return connection_pool


def connection_factory(path=None, options=None):
    """Imports and creates connection pool object from
    the path with the options provided.
    """
    if path is None:
        path = 'django_redis_sdk.connection.ConnectionPool'

    if options is None:
        options = {}

    connection_pool_factory_class = import_string(path)

    return connection_pool_factory_class(options)
