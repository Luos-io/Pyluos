from .generic_motor_controller import GenericMotorController
from .distance import Distance
from .l0_servo import L0Servo
from .encoder import Encoder
from .stepper import Stepper
from .l0_gpio import L0GPIO
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
    'L0GPIO',
    'L0Servo',
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
    'L0GPIO': L0GPIO,
    'l0_servo': L0Servo,
    'DCMotor': DCMotor,
    'encoder': Encoder,
    'Stepper': Stepper,
    'Button': Button,
    'Potentiometer': Potentiometer,
    'Servo': Servo,
    'Relay': Relay,
    'RgbLed': Led,
    'eddy': Eddy,
    'handy': Handy
}
