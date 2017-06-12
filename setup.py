#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

version = imp.load_source('pyrobus.version', 'pyrobus/version.py')


setup(name='pyrobus',
      version=version.version,
      packages=find_packages(),
      install_requires=['future',
                        'websocket-client',
                        'pyserial>3',
                        'requests',
                        'pyzmq',
                        'ipywidgets',
                        ],
      extras_require={
          'tests': ['tornado'],
      },
      )
