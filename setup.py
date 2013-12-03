#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='wymypy-ng',
    version = '2.1',
    description = 'Simple web interface for controlling MPD',
    maintainer = 'Stefan Richter',
    maintainer_email = 'stefan@02strich.de',
    url = 'http://www.02strich.de/',
    packages = find_packages(),
    package_data = {'wymypy': ['static/*.*', 'templates/*.*']},
    install_requires = ['Flask'],
    entry_points = {
        'console_scripts': [
            'wymypy = wymypy.core:main',
        ],
    },
)
