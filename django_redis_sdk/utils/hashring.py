#!/usr/bin/env python3
"""Defines the HashRing utils for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'Node',
    'HashRing'
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


from bisect import insort, bisect
from hashlib import (
    md5,
    sha1,
)

from django.utils.encoding import force_text


DIGITS = 8
BASE_16 = 16


def get_unique_slot_from_key(key):
    """computes the crc of agiven key with md5 algo
    and computes a unique base 16 evaluation of last
    DIGITS (specified by const DIGITS).
    Returns both the base 16 and crc.
    """
    crc = md5(
        key.encode('utf-8')
    ).hexdigest()

    return (
        int(
            crc[-DIGITS:],
            BASE_16
        ),
        crc
    )


class RingNode(object):
    """Defines the Node object for the HashRing
    """

    def __init__(self, name, weighted_slot):
        """Initializes the Node with name and weightage
        """
        self._name = name  # the name (server url in our case)
        self._weighted_slot = weighted_slot  # the slot wrt weightage
        self._key = "%s:%s" % (
            force_text(self._weighted_slot),
            force_text(self._name),
        )  # this identifies the node from other nodes of same name
        self._slot, self._crc = get_unique_slot_from_key(self._key)  # effecticve slot and crc computed

    def __gt__(self, that):
        """Definition for greater than
        This is used inside insort
        """
        if isinstance(that, int):
            return self._slot > that  # compare directly with slot
        elif isinstance(that, RingNode):
            return self._slot > that._slot  # compare with object
        raise TypeError(
            "Cannot compare type '%s' with type '%s'" % (
                type(self),
                type(that),
            )
        )

    def __lt__(self, that):
        """Definition for lesser than
        This is used inside insort
        """
        if isinstance(that, int):
            return self._slot < that  # compare directly with slot
        elif isinstance(that, RingNode):
            return self._slot < that._slot  # compare with object
        raise TypeError(
            "Cannot compare type '%s' with type '%s'" % (
                type(self),
                type(that),
            )
        )


class HashRing(object):
    """Hash ring implementation for Shards configuration
    creates and stores each node in a sorted manner according to server name and weightage.
    """
    def __init__(self, nodes=None, replicas=16):
        """Initializes the HashRing
        @params: nodes - list - list of the servers available in the shard.
        @params: replicas - int - the number of replicas available for each sever in the shard.
        """
        self._replicas = replicas
        self._ring_nodes = []

        if nodes is None:
            nodes = []

        for name in nodes:  # add the node to the ring.
            self.add(name)

    def _add(self, name, weighted_slot):
        """Adds a server node to the ring as RingNode with weightage.
        """
        insort(self._ring_nodes, RingNode(name, weighted_slot))

    def add(self, name, weight=1):
        """Adds a server node with weightage weight weight*replica times to the ring
        """
        for weighted_slot in range(weight * self._replicas):
            self._add(name, weighted_slot)

    def remove(self, name):
        """Removes a server node from the ring node.
        """
        n = len(self._ring_nodes)
        for i, _node in enumerate(reversed(self._ring_nodes)):
            if name == _node._name:
                del self._ring_nodes[n - i - 1]

    def get_node(self, key):
        """For a given key, finds out a bisecting index in the saved ring_nodes and
        returns the appropriate server node of that index.
        """
        ind = bisect(self._ring_nodes, get_unique_slot_from_key(force_text(key))[0]) - 1
        return self._ring_nodes[ind]._name
