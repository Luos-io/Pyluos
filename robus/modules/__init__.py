from .button import Button
from .potard import Potard
from .motor import Motor
from .led import Led


__all__ = [
    'name2mod',
    'Button',
    'Potard',
    'Motor',
    'Led',
]

name2mod = {
    'button': Button,
    'potard': Potard,
    'motor': Motor,
    'led': Led,
}
