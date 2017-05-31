from .distance import Distance
from .button import Button
from .potard import Potard
from .servo import Servo
from .relay import Relay
from .dxl import DxlBus
from .led import Led


__all__ = [
    'name2mod',
    'Distance',
    'Button',
    'DxlBus',
    'Potard',
    'Servo',
    'Relay',
    'Led',
]

name2mod = {
    'distance': Distance,
    'dynamixel': DxlBus,
    'button': Button,
    'potard': Potard,
    'servo': Servo,
    'relay': Relay,
    'led': Led,
}
