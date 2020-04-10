#!/usr/bin/env python3
"""Defines the sharded client for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'ShardedClient',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from collections import (
    defaultdict,
    OrderedDict,
)
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from .base_client import (
    BaseClient,
)
from ..utils import (
    HashRing,
)


class ShardedClient(BaseClient):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

        self._replicas = self._params.get('REPLICAS', 16)
        self._hash_ring = HashRing(nodes=self._servers, replicas=self._replicas)

    def get_client(self, key=None, write=True, **kwargs):
        """
        """
        server = self._hash_ring.get_node(key)
        self.clients[server] = self.clients.get(
            server,
            self.connect(server)
        )
        if kwargs.get('return_index', False):
            return self.clients[server], server
        else:
            return self.clients[server]

    def shard(self, keys, write=False, version=None):
        """Map the keys to its shard namespace and return the mapping
        with original keys
        """
        clients = defaultdict(list)
        for key in keys:
            versioned_key = self.make_key(key, version=version)
            clients[self.get_client(versioned_key, write)].append(key)
        return clients

    def delete_many(self, keys, version=None):
        """Delete multiple value from the cache at once.
        """
        ret_value = []
        clients = self.shard(keys, write=True, version=version)
        for client, s_keys in clients.items():
            ret_value.append(
                super().delete_many(s_keys, version=version, client=client)
            )

        return all(ret_value)

    def get_many(self, keys, version=None):
        """get values for multiple keys at once.
        """
        ret_data = OrderedDict()
        clients = self.shard(keys, version=version)
        for client, s_keys in clients.items():
            ret_data.update(
                super().get_many(s_keys, version=version, client=client)
            )
        return ret_data

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None):
        """set multiple values to the cache at once
        """
        clients = self.shard(data.keys(), write=True, version=version)

        for client, keys in clients.items():
            sub_data = {}
            for k in keys:
                sub_data[k] = data[k]
            super().set_many(sub_data, version=version, client=client, timeout=timeout)
