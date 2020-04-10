#!/usr/bin/env python3
"""Defines the pickle serilizer for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'PickleSerializer',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]

import pickle

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes

from .base_serializer import BaseSerializer


class PickleSerializer(BaseSerializer):
    """Defines the Pickle Serializer
    """

    def __init__(self, options, **kwargs):
        """Initializes the serializer
        """
        super().__init__(options, **kwargs)

        _pickle_version = self._options.get('PICKLE_VERSION', None)
        _pickle_version = kwargs.get('PICKLE_VERSION', None) or _pickle_version or -1

        try:
            self._pickle_version = int(_pickle_version)
        except (ValueError, TypeError):
            raise ImproperlyConfigured(
                "PICKLE_VERSION: expected integer got '%s'" % type(_pickle_version)
            )

    @property
    def pickle_version(self):
        """Pickle version property
        """
        return self._pickle_version

    def serialize(self, value):
        """Serialises the value
        """
        return pickle.dumps(value, self.pickle_version)

    def deserialize(self, value):
        """Deserializes the value
        """
        return pickle.loads(force_bytes(value))
