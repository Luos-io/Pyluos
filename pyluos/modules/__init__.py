from .generic_motor_controller import GenericMotorController
from .distance import Distance
from .encoder import Encoder
from .stepper import Stepper
from .l0_gpio import L0GPIO
from .dxl import Dynamixel
from .button import Button
from .potard import Potard
from .servo import Servo
from .relay import Relay
from .led import Led

__all__ = [
    'name2mod',
    'GenericMotorController',
    'Dynamixel',
    'Distance',
    'Encoder',
    'Stepper',
    'Button',
    'L0GPIO',
    'Potard',
    'Servo',
    'Relay',
    'Led',
]

name2mod = {
    'generic_motor_controller': GenericMotorController,
    'dynamixel': Dynamixel,
    'distance': Distance,
    'GenericIO': L0GPIO,
    'encoder': Encoder,
    'stepper': Stepper,
    'button': Button,
    'potard': Potard,
    'servo': Servo,
    'relay': Relay,
    'led': Led,
}
