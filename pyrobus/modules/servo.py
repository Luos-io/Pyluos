from __future__ import division

from .module import Module


class Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Servo', id, alias, robot)
        self.position = 90

    @property
    def position(self):
        return self._value

    @position.setter
    def position(self, new_pos):
        if new_pos != self._value:
            self._value = new_pos
            self._push_value('value', new_pos)

    @property
    def speed(self):
        return self.position / 180 * 200 - 100

    @speed.setter
    def speed(self, new_speed):
        pos = (new_speed + 100) / 200 * 180
        self.position = pos
