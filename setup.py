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
                        'tornado',
                        'zeroconf',
                        ],
      extras_require={
          'tests': [],
          'topographe': ['pyzmq'],
          'jupyter-integration': ['ipywidgets'],
      },
      entry_points={
          'console_scripts': [
              'pyrobus-wifi-gate = pyrobus.tools.wifi_gate:main',
              'pyrobus-usb-gate = pyrobus.tools.usb_gate:main',
              'pyrobus-usb2ws = pyrobus.tools.usb2ws:main',
              'pyrobus-scratch-broker = pyrobus.tools.scratch_broker:main',
          ],
      },
      )
