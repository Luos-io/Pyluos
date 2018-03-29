#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

version = imp.load_source('pyluos.version', 'pyluos/version.py')


setup(name='pyluos',
      version=version.version,
      packages=find_packages(),
      install_requires=['future',
                        'websocket-client',
                        'pyserial>3',
                        'tornado',
                        'zeroconf',
                        ],
      extras_require={
          'tests': [],
          'topographe': ['pyzmq'],
          'jupyter-integration': ['ipywidgets'],
          'scratch': ['flask', 'Jinja2'],
      },
      entry_points={
          'console_scripts': [
              'pyluos-wifi-gate = pyluos.tools.wifi_gate:main',
              'pyluos-usb-gate = pyluos.tools.usb_gate:main',
              'pyluos-usb2ws = pyluos.tools.usb2ws:main',
              'pyluos-usb2scratch = pyluos.tools.usb2scratch:main',
          ],
      },
      )
