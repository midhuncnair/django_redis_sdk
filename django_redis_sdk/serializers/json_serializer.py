#!/usr/bin/env python3
"""Defines the json serilizer for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'JsonSerializer',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]

import json

from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes, force_text

from .base_serializer import BaseSerializer


class JsonSerializer(BaseSerializer):
    """Defines the Json Serializer
    """

    def __init__(self, options, **kwargs):
        """Initializes the serializer
        """
        super().__init__(options, **kwargs)

    def serialize(self, value):
        """Serializes the value
        """
        return force_bytes(json.dumps(value))

    def deserialize(self, value):
        """Deserializes the value
        """
        return json.loads(force_text(value))
