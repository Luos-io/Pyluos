import logging

from .robot import Robot
from .modules import *


nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
