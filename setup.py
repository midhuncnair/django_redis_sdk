#!/usr/bin/env python3
"""Defines the setup for django-redis-sdk package
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel
python3 -m pip install --user --upgrade twine
python3 -m twine upload dist/*
"""


# from __future__ import


# __all__ = []
__version__ = "0.1.0.0"
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import setuptools


with open("README.rst", 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name="django-redis-sdk",
    version="0.1.0.0",
    author="Midhun C Nair",
    author_email="midhunch@gmail.com",
    description="Django Redis sdk",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/midhuncnair/django_redis_sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5.9',
)
