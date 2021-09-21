#!/usr/bin/env python

import imp

from setuptools import setup, find_packages

version = imp.load_source('pyluos.version', 'pyluos/version.py')

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pyluos',
      version=version.version,
      author="Luos",
      author_email="hello@luos.io",
      url="https://docs.luos.io/pages/high/pyluos.html",
      description="Python library to set the high level behavior of your device based on Luos embedded system.",
      license='MIT',
      packages=find_packages(),
      install_requires=['future',
                        'websocket-client',
                        'pyserial>3',
                        'SimpleWebSocketServer',
                        'zeroconf',
                        'numpy',
                        'anytree',
                        'crc8'
                        ],
      extras_require={
          'tests': ['pytest', 'flake8'],
          'jupyter-integration': ['ipywidgets'],
      },
      entry_points={
          'console_scripts': [
              'pyluos-wifi-gate = pyluos.tools.wifi_gate:main',
              'pyluos-usb-gate = pyluos.tools.usb_gate:main',
              'pyluos-usb2ws = pyluos.tools.usb2ws:main',
              'pyluos-bootloader = pyluos.tools.bootloader:main',
              'pyluos-shell = pyluos.tools.shell:main',
              'pyluos-discover = pyluos.tools.discover:main'
          ],
      },
      )
