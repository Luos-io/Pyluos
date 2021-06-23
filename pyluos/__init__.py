import logging

from .device import Device
from .device import Sniffer
from .containers import *

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
