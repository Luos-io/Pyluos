from .generic_motor_controller import GenericMotorController
from .distance import Distance
from .l0_gpio import GPIO
from .dc_motor import DCMotor
from .dxl import DynamixelMotor
from .button import Button
from .potentiometer import Potentiometer
from .servo import Servo
from .led import Led
from .handy import Handy
from .imu import Imu


__all__ = [
    'name2mod',
    'GenericMotorController',
    'DynamixelMotor',
    'Distance',
    'Button',
    'GPIO',
    'Potentiometer',
    'Servo',
    'Led',
    'DCMotor',
    'Handy',
    'Imu' ,
]

name2mod = {
    'GenericMotor': GenericMotorController,
    'DynamixelMotor': DynamixelMotor,
    'DistanceSensor': Distance,
    'GPIO': GPIO,
    'DCMotor': DCMotor,
    'Button': Button,
    'Potentiometer': Potentiometer,
    'Servo': Servo,
    'RgbLed': Led,
    'Handy': Handy,
    'Imu': Imu
}
