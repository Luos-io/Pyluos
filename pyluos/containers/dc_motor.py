from __future__ import division

from .container import Container, interact


class DCMotor(Container):
    def __init__(self, id, alias, device):
        Container.__init__(self, 'DCMotor', id, alias, device)

    @property
    def power_ratio(self):
        self._value

    @power_ratio.setter
    def power_ratio(self, s):
        s = min(max(s, -100.0), 100.0)
        self._value = s
        self._push_value("power_ratio",s)

    def _update(self, new_state):
        Container._update(self, new_state)

    def control(self):
        def move(power_ratio):
            self.power_ratio = power_ratio

        return interact(move, power_ratio=(-100.0, 100.0, 1.0))
