#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Marco Cieno"
__copyright__ = "Copyright 2019, Marco Cieno"
__license__ = "MIT"
__email__ = "cieno.marco@gmail.com"

from setuptools import setup


setup(
    name='spotify-sort-by-release',
    description='Sort Spotify playlists by release date of tracks.',
    version="1.0.2",
    license=__license__,
    author=__author__,
    author_email=__email__,
    url='https://github.com/mcieno/spotify-sort-by-release',
    package_dir={'spotify_sort_by_release': 'spotify_sort_by_release'},
    packages=['spotify_sort_by_release'],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'spotify-sort-by-release = spotify_sort_by_release:main',
        ]
    },
)
