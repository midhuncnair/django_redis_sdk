#!/usr/bin/env python3
"""Defines the base serializer for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'BaseSerializer',
    'DummySerializer',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


class BaseSerializer:
    """Defines the Base serializer
    """

    def __init__(self, options, **kwargs):
        """Initializes the serializer
        """
        self._options = options

    def serialize(self, value):
        """Serializes the value
        needs to be implemented in inheriting class
        """
        raise NotImplementedError("BaseClass")

    def deserialize(self, value):
        """Deserializes the value
        needs to be implemented in inheriting class
        """
        raise NotImplementedError("BaseClass")

    class Meta:
        abstract = True


class DummySerializer(BaseSerializer):
    """Defines the Dummy serializer
    can be used if no serialization is needed.
    """

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value
