#!/usr/bin/env python3
"""Defines the Exception for django-redis-sdk backends
"""


# from __future__ import


__all__ = [
    'ConnectionException',
]
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


class ConnectionException(Exception):
    """Custom connection Exception
    """

    def __init__(self, client, *args, from_error=None, **kwargs):
        """Initializes the custom error
        """
        self.client = client
        self.from_error = from_error
        self.error_class = (
            self.from_error.__class__.__name__
            if self.from_error is not None
            else "DjangoRedisSDKConnectionError"
        )
        self.message = (
            str(self.from_error)
            if self.from_error is not None
            else "Connection Error connecting Redis"
        )

    def __str__(self):
        """Overwrite the error message
        """
        return "%s: %s" % (
            self.error_class,
            self.message
        )
