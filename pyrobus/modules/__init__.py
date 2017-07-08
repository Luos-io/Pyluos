from .distance import Distance
from .stepper import Stepper
from .dxl import Dynamixel
from .button import Button
from .potard import Potard
from .servo import Servo
from .relay import Relay
from .led import Led

__all__ = [
    'name2mod',
    'Dynamixel',
    'Distance',
    'Stepper',
    'Button',
    'Potard',
    'Servo',
    'Relay',
    'Led',
]

name2mod = {
    'dynamixel': Dynamixel,
    'distance': Distance,
    'stepper': Stepper,
    'button': Button,
    'potard': Potard,
    'servo': Servo,
    'relay': Relay,
    'led': Led,
}
