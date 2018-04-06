import logging

from .robot import Robot
from .modules import *

from .eddy import Eddy
from .ergo import ErgoJr
from .handy import Handy

nh = logging.NullHandler()
logging.getLogger(__name__).addHandler(nh)
