from .generic_motor_controller import GenericMotorController
from .distance import Distance
from .encoder import Encoder
from .stepper import Stepper
from .l0_gpio import GPIO
from .dc_motor import DCMotor
from .dxl import DynamixelMotor
from .button import Button
from .potentiometer import Potentiometer
from .servo import Servo
from .relay import Relay
from .led import Led
from .eddy import Eddy
from .handy import Handy


__all__ = [
    'name2mod',
    'GenericMotorController',
    'DynamixelMotor',
    'Distance',
    'Encoder',
    'Stepper',
    'Button',
    'GPIO',
    'Potentiometer',
    'Servo',
    'Relay',
    'Led',
    'DCMotor',
    'Eddy',
    'Handy',
]

name2mod = {
    'GenericMotor': GenericMotorController,
    'DynamixelMotor': DynamixelMotor,
    'DistanceSensor': Distance,
    'GPIO': GPIO,
    'DCMotor': DCMotor,
    'encoder': Encoder,
    'Stepper': Stepper,
    'Button': Button,
    'Potentiometer': Potentiometer,
    'Servo': Servo,
    'Relay': Relay,
    'RgbLed': Led,
    'eddy': Eddy,
    'Handy': Handy
}
