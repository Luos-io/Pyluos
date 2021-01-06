from .gate import Gate
from .generic_motor_controller import GenericMotorController
from .distance import Distance
from .l0_gpio import GPIO
from .dc_motor import DCMotor
from .state import State
from .angle import Angle
from .servo import Servo
from .color import Color
from .handy import Handy
from .imu import Imu
from .stepper import Stepper
from .power_switch import PowerSwitch
from .light_sensor import LightSensor
from .controller_motor import ControllerMotor
from .void import Void
from .load import Load
from .voltage import Voltage
from .unknown import Unknown


__all__ = [
    'name2mod',
    'Gate',
    'GenericMotorController',
    'Distance',
    'State',
    'GPIO',
    'Angle',
    'Servo',
    'Color',
    'DCMotor',
    'Handy',
    'Imu' ,
    'Stepper',
    'PowerSwitch',
    'LightSensor',
    'ControllerMotor',
    'Void',
    'Load',
    'Voltage',
    'Unknown'
]

name2mod = {
    'Gate': Gate,
    'GenericMotor': GenericMotorController,
    'DistanceSensor': Distance,
    'GPIO': GPIO,
    'DCMotor': DCMotor,
    'State': State,
    'Angle': Angle,
    'Servo': Servo,
    'Color': Color,
    'Handy': Handy,
    'Imu': Imu,
    'Stepper' : Stepper,
    'PowerSwitch' : PowerSwitch,
    'LightSensor' : LightSensor,
    'ControllerMotor' : ControllerMotor,
    'Void' : Void,
    'Load' : Load,
    'Voltage' : Voltage,
    'Unknown' : Unknown
}
