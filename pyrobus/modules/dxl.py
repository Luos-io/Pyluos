from __future__ import division

from ipywidgets import interact

from .module import Module


class Dynamixel(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)

        self._present_position = None
        self._goal_position = None
        self._moving_speed = None
        self._compliant = None

    @property
    def present_position(self):
        return self._present_position

    @property
    def position(self):
        return self.present_position

    @property
    def goal_position(self):
        return self._goal_position

    @goal_position.setter
    def goal_position(self, new_pos):
        if new_pos != self._goal_position:
            self._goal_position = new_pos
            self._push_value('goal_position', self._goal_position)

    @property
    def moving_speed(self):
        return self._moving_speed

    @moving_speed.setter
    def moving_speed(self, new_speed):
        if new_speed != self._moving_speed:
            self._moving_speed = new_speed
            self._push_value('moving_speed', self._moving_speed)

    @property
    def compliant(self):
        return self._compliant == 1

    @compliant.setter
    def compliant(self, new_compliancy):
        if new_compliancy != self._compliant:
            self._compliant = 1 if new_compliancy else 0
            self._push_value('compliant', self._compliant)

    def _update(self, new_state):
        new_pos = new_state['present_position']

        if new_pos != self._present_position:
            self._pub_event('moved', self._present_position, new_pos)
            self._present_position = new_pos

    def control(self):
        def move(position):
            self.position = position

        return interact(move, position=(-180.0, 180.0, 0.1))
