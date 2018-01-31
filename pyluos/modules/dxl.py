from __future__ import division

from .module import Module, interact


class Dynamixel(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)

        # Read
        self._position = None

        # Write
        self._target_position = None
        self._target_speed = None
        self._compliant = None
        self._wheel = None

    @property
    def position(self):
        """ Current position in degrees. """
        return self._position

    @property
    def target_position(self):
        """ Target position in degrees. """
        return self._target_position

    @target_position.setter
    def target_position(self, new_pos):
        if new_pos != self._target_position:
            self._target_position = new_pos
            self._push_value('target_position', self._target_position)

    @property
    def target_speed(self):
        """ Speed in rpm. """
        return self._target_speed

    @target_speed.setter
    def target_speed(self, new_speed):
        if new_speed != self._target_speed:
            self._target_speed = new_speed
            self._push_value('target_speed', self._target_speed)

    @property
    def compliant(self):
        return (self._compliant == 1
                if self._compliant is not None else
                None)

    @compliant.setter
    def compliant(self, new_compliancy):
        if new_compliancy != self._compliant:
            self._compliant = 1 if new_compliancy else 0
            self._push_value('compliant', self._compliant)

    @property
    def wheel_mode(self):
        return (self._wheel == 1
                if self._wheel is not None else
                None)

    @wheel_mode.setter
    def wheel_mode(self, new_mode):
        if new_mode != self._wheel:
            self._wheel = 1 if new_mode else 0
            self._push_value('wheel', self._wheel)

            if self._wheel == 0:
                self._compliant = 1

    def _update(self, new_state):
        new_pos = new_state['position']

        if new_pos != self._position:
            self._pub_event('moved', self._position, new_pos)
            self._position = new_pos

    def control(self):
        def move(position):
            self.target_position = position

        return interact(move, position=(-180.0, 180.0, 0.1))
