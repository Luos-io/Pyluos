from __future__ import division

from .module import Module, interact


class Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Servo', id, alias, robot)
        self._max_angle = 180.0
        self._min_pulse = 0.0005
        self._max_pulse = 0.0015
        self._angle = 0.0

    @property
    def position(self):
        return self._angle

    @position.setter
    def position(self, new_pos):
        if new_pos != self._angle:
            self._angle = new_pos
            self._push_value('target_rot_position', new_pos)

    @property
    def max_angle(self):
        return self._max_angle

    @max_angle.setter
    def max_angle(self, new):
        if new != self._max_angle:
            self._max_angle = new
            param = [self._max_angle, self._min_pulse, self._max_pulse]
            self._push_value('parameters', param)

    @property
    def min_pulse(self):
        return self._min_pulse

    @min_pulse.setter
    def min_pulse(self, new):
        if new != self._min_pulse:
            self._min_pulse = new
            param = [self._max_angle, self._min_pulse, self._max_pulse]
            self._push_value('parameters', param)

    @property
    def max_pulse(self):
        return self._max_pulse

    @max_pulse.setter
    def max_pulse(self, new):
        if new != self._max_pulse:
            self._max_pulse = new
            param = [self._max_angle, self._min_pulse, self._max_pulse]
            self._push_value('parameters', param)

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def move(position):
            self.position = position

        return interact(move, position=(0, 180, 1))
