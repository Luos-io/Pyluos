import logging

from .device import Device
from .containers import *

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
