Django Redis SDK
================


1.0.0.0
-------

* General Bug Fixes

0.1.1.0
-------

* General Bug Fixes

0.1.0.0
-------

Django Redis SDK: A SDK for connecting to Redis server from Django.

* Supports both TCP socket connection and Unix socket connection
* Plug and play architecture.
* Everything is configurable.
* Supports base client connection in master/slave configuration (Out of box with ``DjangoRedisSDKCache`` backend class).
* Supports sharded client connection configuration (Out of box with ``DjangoRedisSDKShrededCache`` backend class).
* You have Dummy Cache backend for just testing or monkey patching (Achieved using ``DjangoRedisSDKDummyCache`` backend class).
* A wrapper around redis package.
* Pluggable CLIENT, REDIS_CLIENT, PARSER, COMPRESSOR, SERIALIZER,
* Out of the box support for Master-Slave and Shard client.
* supports all default apis.
* supports redis cluster; **requires** redis-py-cluster



Dependancies
============

* `redis`_>=3.0.1
* `django`_>= 2.2
* `hiredis`_>=1.0.1 (if configured to use)
* `python`_>=3.5.9
* `redis-py-cluster`_>=2.0.0 (if configured to use)



QuickStart
==========

Installation and Basic Configuration
------------------------------------

1. Install Django Redis SDK by running ``pip install django-redis-sdk``.
2. Make changes in you settings file to accommodate the cache settings.

.. code:: python

    # DjangoRedisSDKCache -> Master - slave connection
    CACHES = {
        'default': {
            'BACKEND': 'django_redis_sdk.DjangoRedisSDKCache',
            'KEY_PREFIX': 'production',
            'LOCATION': [
                '[<scheme>://][:password@]<host>:<port>',  # Master
                '[<scheme>://][:password@]<host>:<port>',  # slave 1
                '[<scheme>://][:password@]<host>:<port>',  # slave 2
                # ...
            ],
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': 'passwd',
                'CLIENT_CLASS': 'django_redis_sdk.clients.BaseClient',
                'PARSER_CLASS': 'redis.connection.DefaultParser',
                'CONNECTION_POOL_CLASS': 'redis.connection.ConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 14,
                },
                'SERIALIZER_CLASS': 'django_redis_sdk.serializers.PickleSerializer',
                'PICKLE_VERSION': -1,
                'SERIALIZER_CLASS_KWARGS': {
                    'PICKLE_VERSION': -1,
                },
                'COMPRESSOR_CLASS': 'django_redis_sdk.compressors.DummyCompressor',
                'COMPRESS_LEVEL': 5,
                'COMPRESSOR_CLASS_KWARGS': {
                    'COMPRESS_LEVEL': 5,
                },
                'REDIS_CLIENT_CLASS': 'redis.client.StrictRedis',
                'REDIS_CLIENT_KWARGS': {},
                'SOCKET_CONNECT_TIMEOUT': 5,  # in seconds; 5000 milliseconds,
                'SOCKET_TIMEOUT': 1,  # in seconds; 1000 milliseconds,
                'HANDLE_EXCEPTIONS': True,
                'LOG_EXCEPTIONS': True,
                'LOGGER_NAME': 'django_redis_sdk',
            }
        }
    }

    # DjangoRedisSDKShrededCache -> Shard
    CACHES = {
        'default': {
            'BACKEND': 'django_redis_sdk.DjangoRedisSDKShrededCache',
            'KEY_PREFIX': 'production',
            'LOCATION': [
                '[<scheme>://][:password@]<host>:<port>[/db]',  # read-write 1
                '[<scheme>://][:password@]<host>:<port>[/db]',  # read-write 2
                '[<scheme>://][:password@]<host>:<port>[/db]',  # read-write 3
                # ...
            ],
            'OPTIONS': {
                'DB': 0,
                'PASSWORD': 'passwd',
                'CLIENT_CLASS': 'django_redis_sdk.clients.BaseClient',
                'PARSER_CLASS': 'redis.connection.DefaultParser',
                'CONNECTION_POOL_CLASS': 'redis.connection.ConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 14,
                },
                'SERIALIZER_CLASS': 'django_redis_sdk.serializers.PickleSerializer',
                'PICKLE_VERSION': -1,
                'SERIALIZER_CLASS_KWARGS': {
                    'PICKLE_VERSION': -1,
                },
                'COMPRESSOR_CLASS': 'django_redis_sdk.compressors.DummyCompressor',
                'COMPRESS_LEVEL': 5,
                'COMPRESSOR_CLASS_KWARGS': {
                    'COMPRESS_LEVEL': 5,
                },
                'REDIS_CLIENT_CLASS': 'redis.client.StrictRedis',
                'REDIS_CLIENT_KWARGS': {},
                'SOCKET_CONNECT_TIMEOUT': 5,  # in seconds; 5000 milliseconds,
                'SOCKET_TIMEOUT': 1,  # in seconds; 1000 milliseconds,
                'HANDLE_EXCEPTIONS': True,
                'LOG_EXCEPTIONS': True,
                'LOGGER_NAME': 'django_redis_sdk',
            }
        }
    }

    # Cluster -> cluster
    CACHES = {
        'default': {
            'BACKEND': 'django_redis_sdk.DjangoRedisSDKCache',
            'KEY_PREFIX': 'production',
            'LOCATION': [
                '[<scheme>://]<host>:<port>[/db]',  # cluster 1
                '[<scheme>://]<host>:<port>[/db]',  # cluster 2
                '[<scheme>://]<host>:<port>[/db]',  # cluster 3
                # ...
            ],
            'OPTIONS': {
                'PARSER_CLASS': 'redis.connection.DefaultParser',
                'CONNECTION_POOL_CLASS': 'rediscluster.connection.ClusterConnectionPool',
                'CONNECTION_POOL_CLASS_KWARGS': {
                    'max_connections': 14,
                    'skip_full_coverage_check': True,  # some redis implementation has disabled the CONFIG
                },
                'SERIALIZER_CLASS': 'django_redis_sdk.serializers.PickleSerializer',
                'PICKLE_VERSION': -1,
                'SERIALIZER_CLASS_KWARGS': {
                    'PICKLE_VERSION': -1,
                },
                'COMPRESSOR_CLASS': 'django_redis_sdk.compressors.DummyCompressor',
                'COMPRESS_LEVEL': 5,
                'COMPRESSOR_CLASS_KWARGS': {
                    'COMPRESS_LEVEL': 5,
                },
                'REDIS_CLIENT_CLASS': 'rediscluster.RedisCluster',
                'REDIS_CLIENT_KWARGS': {},
                'SOCKET_CONNECT_TIMEOUT': 5,  # in seconds; 5000 milliseconds,
                'SOCKET_TIMEOUT': 1,  # in seconds; 1000 milliseconds,
                'HANDLE_EXCEPTIONS': True,
                'LOG_EXCEPTIONS': True,
                'LOGGER_NAME': 'django_redis_sdk',
            }
        }
    }



Basic Usage
===========

Django Redis SDK has same backend apis as Django with some additions

example::

    >>>from django.core.cache import cache
    >>>cache.set('foo', 'bar', timeout=5)  # key = foo, value = 'bar' and valid for 5 seconds
    >>>cache.ttl('foo')
    5
    >>>cache.get('foo')
    bar
    >>>cache.set_many({'foo':'boo', 'bar': 'baz'})
    >>>cache.get_many(['foo', 'baz'])
    OrderedDict([('foo', 'boo'), ('bar', 'baz')])
    >>>cache.get_or_set('faz', 'baz', timeout=5)  # key = 'faz', dafault='baz' and valid for 5 seconds
    baz  # since a key is not the value will be first set and then returned.
    >>>import random
    >>>cache.get_or_set('fazo', random.random, timeout=5)  # the default can take a callable also as input.
    0.32685093104745067  # since the key is not set the random.random is called and the value is set and returned.


BACKEND values
--------------

*  ``django_redis_sdk.DjangoRedisSDKCache``  # for single namespace
*  ``django_redis_sdk.DjangoRedisSDKShrededCache``  # for sharded namespace

LOCATION values
---------------

* String: comma seperated string for multiple server, single string value for single server.
* List: single server in list for single server, multiple list value for multiple servers.
* scheme:
        ``host:port``  -> ``127.0.0.1:6379``  -> db defaults to DB option value or '0'.
        ``host:port/db``  -> ``127.0.0.1:6379/1``  -> db is taken from url.
        ``:password@host:port``  -> ``:myPasswd@127.0.0.1:6379/1``  -> password taken from url as opposed to None or value in options.
        ``/path/to/the/unix/socket``  -> ``/etc/redis/connection.sock``  -> uses unix socket for communication
        ``url_scheme://<combinations of above values>``

        *  ``redis://:passwd@127.0.0.0:6379/1``
        *  ``rediss://localhost:6379/1`` --> ssl connection
        * ``unix://path/to/the/unix/socket`` --> unix socket connection

        NOTE: if url_scheme is not specified, we try to best assume the url_scheme; however it is best to provide the scheme.


OPTIONS
-------

DB
---

**Default**: ``0``

The URL specified db has precedence over this one.
If you with to see the cached values through redis-cli please select the db you assigned before querying by ``SELECT <db>``


PASSWORD
--------

**Default**: ``None``

The URL specified password has precedence over this one.
Ideally the REDIS server will be deployed inside a secure network with no access from outside; So, there wouldn't be a password set in that case.
But if you have password set, Please configure it here.


CLIENT_CLASS
------------

**Default**: According to the BACKEND.

*  ``django_redis_sdk.clients.BaseClient``  # used as default in ``DjangoRedisSDKCache`` backend
*  ``django_redis_sdk.clients.ShardedClient``  # used as default in ``DjangoRedisSDKShrededCache`` backend


PARSER_CLASS
------------

**Default**: ``redis.connection.DefaultParser``

* ``redis.connection.PythonParser``
* ``redis.connection.HiredisParser``  # requires hiredis ``pip install hiredis``
* ``redis.connection.DefaultParser``  # automatically chooses between python or hiredis (if hiredis available then hiredis else python)


CONNECTION_POOL_CLASS
---------------------

**Default**: ``redis.connection.ConnectionPool``

Apply kwargs if any through ``CONNECTION_POOL_CLASS_KWARGS`` options for this class.

* ``redis.connection.ConnectionPool``  # takes additional kwargs ``max_connections``
* ``redis.connection.BlockingConnectionPool``  # takes additional kwargs ``max_connections``, ``timeout``
* ``rediscluster.connection.ClusterConnectionPool``  # requires redis-py-cluster ``pip install redis-py-cluster``

SERIALIZER_CLASS
----------------

**Default**: ``django_redis_sdk.serializers.PickleSerializer``

Apply kwargs if any through ``SERIALIZER_CLASS_KWARGS`` options for this class.

*  ``django_redis_sdk.serializers.PickleSerializer``  # python pickle, takes ``PICKLE_VERSION`` options; defaults to -1
*  ``django_redis_sdk.serializers.DummySerializer``  # no serialization
*  ``django_redis_sdk.serializers.JsonSerializer``  # json.loads and json.dumbs


PICKLE_VERSION
--------------

**Default**: ``-1``  # for custom SERIALIZER_CLASS you should configure the default value.

Used along with ``SERIALIZER_CLASS=django_redis_sdk.serializers.PickleSerializer``; Otherwise no effect.


COMPRESSOR_CLASS
----------------

**Default**: ``django_redis_sdk.compressors.DummyCompressor``

Apply kwargs if any through ``COMPRESSOR_CLASS_KWARGS`` options for this class.

*  ``django_redis_sdk.compressors.DummyCompressor``  # no compression
*  ``django_redis_sdk.compressors.ZlibCompressor``  # requires zlib to compress and decompress, takes ``COMPRESS_LEVEL``

COMPRESS_LEVEL
--------------

**Default**: ``5``  # for custom COMPRESSOR_CLASS you should configure the default value.

* Allowed values ``0`` to ``9``
* ``0`` no compression.
* ``9`` full compression.


REDIS_CLIENT_CLASS
------------------

**Default**: ``redis.client.Redis``

Apply kwargs if any through ``REDIS_CLIENT_KWARGS`` option for this class.

*  ``redis.client.Redis``
*  ``redis.client.StrictRedis``  # in redis>=3.4.1 this is same as ``redis.client.Redis``
*  ``rediscluster.RedisCluster``  # requires `redis-py-cluster`_ ; install using ``pip install redis-py-cluster``. For cluster support.


SOCKET_CONNECT_TIMEOUT
----------------------

**Default**: ``None``  # means wait infinitely

The maximum allowed time to wait to make a connection.


SOCKET_TIMEOUT
--------------

**Default**: ``None``  # means wait infinitely

The maximum allowed time to wait for an operation to wait (wait for response once after the connection is made).


HANDLE_EXCEPTIONS
-----------------

**Default**: ``False``

Whether to handle exceptions gracefully or propagate it?
The exceptions defined in ``django_redis_sdk.utils.EXCEPTIONS_TO_HANDLE`` are caught and handled gracefully


LOG_EXCEPTIONS
--------------

**Default**: ``False``

Whether to log the exceptions While handling the exceptions.
Used along with ``HANDLE_EXCEPTIONS``.


LOGGER_NAME
-----------

**Default**: ``__name__``

Defines which python logger to send the logs to while logging the exceptions.
Used along with LOG_EXCEPTIONS and HANDLE_EXCEPTIONS.

.. _redis: http://github.com/antirez/redis/
.. _hiredis: http://github.com/antirez/hiredis/
.. _python: http://python.org
.. _django: https://www.djangoproject.com/
.. _redis-py-cluster: https://github.com/Grokzen/redis-py-cluster
