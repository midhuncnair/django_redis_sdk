#!/usr/bin/env python3
"""Defines the setup for django-redis-sdk package
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel
python3 -m pip install --user --upgrade twine
python3 -m twine check dist/*  # fix the issue if any
python3 -m twine upload dist/*
"""


# from __future__ import


# __all__ = []
__version__ = '1.0.0.0'
__author__ = "Midhun C Nair<midhunch@gmail.com>"
__maintainers__ = [
    "Midhun C Nair<midhunch@gmail.com>",
]


import setuptools


def read_text(path):
    """Read the text from the given file and
    return
    """
    with open(path, 'r') as fh:
        data = fh.read()

    return data


setuptools.setup(
    name="django-redis-sdk",
    version='1.0.0.0',
    author="Midhun C Nair",
    author_email="midhunch@gmail.com",
    description="Django Redis sdk",
    long_description=read_text("README.rst"),
    long_description_content_type="text/x-rst",
    url="https://github.com/midhuncnair/django_redis_sdk",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5.9',
    license="MIT LICENSE",
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst", "LICENSE"],
    },
    install_requires=[
        "docutils>=0.3",
        "redis>=3.0.1",
        "django>=2.2",
    ],
    keywords="django, redis, django-redis-sdk, redis-cache, cache, django-cache, django-redis-cache",
)
