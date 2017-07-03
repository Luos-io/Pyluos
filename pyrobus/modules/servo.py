from __future__ import division

from .module import Module, interact


class Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Servo', id, alias, robot)

    @property
    def target_position(self):
        return self._value

    @target_position.setter
    def target_position(self, new_pos):
        if new_pos != self._value:
            self._value = new_pos
            self._push_value('target_position', new_pos)

    @property
    def target_speed(self):
        return self.target_position / 180 * 200 - 100

    @target_speed.setter
    def target_speed(self, new_speed):
        pos = (new_speed + 100) / 200 * 180
        self.target_position = pos

    def control(self):
        def move(position):
            self.target_position = position

        return interact(move, position=(0, 180, 1))
