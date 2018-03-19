from __future__ import division

from .module import Module


class DCMotor(object):
    def __init__(self, name, delegate):
        self._name = name
        self._delegate = delegate
        self._speed = None

    @property
    def name(self):
        return self._name

    @property
    def speed(self):
        self._speed

    @speed.setter
    def speed(self, s):
        s = min(max(s, -1.0), 1.0)

        if s != self._speed:
            self._speed = s
            field = self.name.replace('m', 's')
            self._delegate._push_value(field, self._speed)


class L0DCMotor(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0DCMotor', id, alias, robot)

        self.m1 = DCMotor('m1', self)
        self.m2 = DCMotor('m2', self)
