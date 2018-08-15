from __future__ import division

from .module import Module, interact


class Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Servo', id, alias, robot)

    @property
    def position(self):
        return self._value

    @position.setter
    def position(self, new_pos):
        if new_pos != self._value:
            self._value = new_pos
            self._push_value('target_position', new_pos)

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def move(position):
            self.position = position

        return interact(move, position=(0, 180, 1))
