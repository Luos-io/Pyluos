from __future__ import division

from ipywidgets import interact

from .module import Module


class Dynamixel(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)
        self._value = None

    @property
    def position(self):
        return self._value

    @position.setter
    def position(self, new_pos):
        if new_pos != self._value:
            self._value = new_pos
            self._push_value('value', new_pos)

    def control(self):
        def move(position):
            self.position = position

        return interact(move, position=(-180.0, 180.0, 0.1))
