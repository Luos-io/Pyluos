#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

version = imp.load_source('robus.version', 'robus/version.py')


setup(name='robus',
      version=version.version,
      packages=find_packages(),
      install_requires=['future',
                        'websocket-client',
                        'pyserial>3',
                        'requests',
                        ],
      )
