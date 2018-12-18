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
from .stepper import Stepper
from .power_switch import PowerSwitch
from .light_sensor import LightSensor
from .controlled_motor import ControlledMotor


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
    'Stepper',
    'PowerSwitch',
    'LightSensor',
    'ControlledMotor'
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
    'Imu': Imu,
    'Stepper' : Stepper,
    'PowerSwitch' : PowerSwitch,
    'LightSensor' : LightSensor,
    'ControlledMotor' : ControlledMotor
}
