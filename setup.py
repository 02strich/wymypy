#!/usr/bin/env python
from setuptools import setup

setup(name='wymypy',
    version = '2.0',
    description = 'Simple web interface for controlling MPD',
    maintainer = 'Stefan Richter',
    maintainer_email = 'stefan@02strich.de',
    packages = ['wymypy'],
    install_requires = ['Flask'],
    entry_points = {
        'console_scripts': [
            'wymypy = wymypy.core:main',
        ],
    },
)