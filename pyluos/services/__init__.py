from .state import State
from .color import Color
from .motor import Motor
from .servoMotor import ServoMotor
from .angle import Angle
from .distance import Distance
from .gate import Gate
from .imu import Imu
from .light import Light
from .void import Void
from .load import Load
from .voltage import Voltage
from .pipe import Pipe
from .unknown import Unknown


__all__ = [
    'name2mod',
    'State',
    'Color',
    'Motor',
    'ServoMotor',
    'Angle',
    'Distance',
    'Gate',
    'Imu' ,
    'Light',
    'Void',
    'Load',
    'Voltage',
    'Pipe',
    'Unknown'
]

name2mod = {
    'State': State,
    'Color': Color,
    'Motor': Motor,
    'ServoMotor': ServoMotor,
    'Angle': Angle,
    'Distance': Distance,
    'Gate': Gate,
    'Imu': Imu,
    'Light' : Light,
    'Void' : Void,
    'Load' : Load,
    'Voltage' : Voltage,
    'Pipe' : Pipe,
    'Unknown' : Unknown
}
