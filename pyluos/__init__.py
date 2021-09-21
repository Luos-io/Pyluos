import logging

from .device import Device
from .services import *

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
