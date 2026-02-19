import logging

from .device import Device, map_custom_service
from .services import *

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
