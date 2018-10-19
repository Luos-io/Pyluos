from .module import Module, interact

class DynamixelMotor(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'DynamixelMotor', id, alias, robot)
        # Read
        self.position = None

        # Write
        self._target_position = None
        self._moving_speed = None
        self._compliant = None
        self._wheel_mode = None

    def _update(self, new_state):
        Module._update(self, new_state)

        if 'position' in new_state:
            self.position = new_state['position']

    @property
    def target_position(self):
        return self._target_position

    @target_position.setter
    def target_position(self, target_position):
        if target_position != self._target_position and self._compliant == False:
            self._push_value('target_position', target_position)
            self._target_position = target_position

    @property
    def moving_speed(self):
        return self._moving_speed

    @moving_speed.setter
    def moving_speed(self, moving_speed):
        if moving_speed != self._moving_speed:
            self._push_value('target_speed', moving_speed)
            self._moving_speed = moving_speed

    @property
    def compliant(self):
        return self._compliant

    @compliant.setter
    def compliant(self, compliant):
        self._push_value('compliant', compliant)
        self._compliant = compliant

    @property
    def wheel_mode(self):
        return self._wheel_mode

    @wheel_mode.setter
    def wheel_mode(self, wheel_mode):
        if wheel_mode != self._wheel_mode:
            self._push_value('wheel_mode', wheel_mode)
            self._wheel_mode = wheel_mode

    # notebook things
    def control(self):
        def change_position(target_position):
            self.target_position = target_position

        return interact(change_position, target_position=(-150.0, 150.0, 1.0))
