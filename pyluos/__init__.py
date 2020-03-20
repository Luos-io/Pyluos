import logging

from .device import Device
from .modules import *

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
