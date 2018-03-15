from __future__ import division

from .module import Module, interact


class XL320(object):
    def __init__(self, name, delegate):
        self._name = name
        self._delegate = delegate
        self._target_pos = None

    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return from_dxl_pos(self._position)

    @property
    def target_position(self):
        return self._target_pos

    @target_position.setter
    def target_position(self, new_pos):
        if new_pos != self._target_pos:
            self._delegate._push_value(self.name, to_dxl_pos(new_pos))
            self._target_pos = new_pos


def to_dxl_pos(pos):
    pos = min(max(pos, -150.0), 149.9)
    return int((150.0 + pos) / 300.0 * 1024)


def from_dxl_pos(pos):
    pos = min(max(pos, 0), 1023)
    return (pos / 1024.0) * 300.0 - 150.0


class Dynamixel(Module):
    MAX_MOTOR = 20

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)
        self._setup = False
        self.motors = []

    def _update(self, new_state):
        if not self._setup:
            motors = ['m{}'.format(i) for i in range(self.MAX_MOTOR)]
            motors = [m for m in motors if m in new_state]
            for m in motors:
                setattr(self, m, XL320(m, self))
                self.motors.append(getattr(self, m))

            self._setup = True

        for m in self.motors:
            if m.name in new_state:
                m._position = new_state[m.name]
