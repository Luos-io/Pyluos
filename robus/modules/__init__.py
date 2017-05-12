from .distance import Distance
from .button import Button
from .potard import Potard
from .motor import Motor
from .relay import Relay
from .led import Led


__all__ = [
    'name2mod',
    'Distance',
    'Button',
    'Potard',
    'Motor',
    'Relay',
    'Led',
]

name2mod = {
    'distance': Distance,
    'button': Button,
    'potard': Potard,
    'motor': Motor,
    'relay': Relay,
    'led': Led,
}
