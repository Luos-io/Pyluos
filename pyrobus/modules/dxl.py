from collections import defaultdict

from .module import Module


class DxlBus(Module):
    possible_events = {'moved'}

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Dynamixel', id, alias, robot)

        self._pos = self._speed = None

        self._reg = defaultdict(lambda: None)

        self.goal_position = 0
        self.moving_speed = 0
        self.torque_limit = 100
        self.compliant = False

    @property
    def present_position(self):
        return self._pos

    @property
    def present_speed(self):
        return self._speed

    @property
    def goal_position(self):
        return self._reg['goal']

    @goal_position.setter
    def goal_position(self, new_goal):
        if new_goal != self._reg['goal']:
            self._reg['goal'] = new_goal
            self._push_value('goal_position', new_goal)

    @property
    def moving_speed(self):
        return self._reg['speed']

    @moving_speed.setter
    def moving_speed(self, new_speed):
        if new_speed != self._reg['speed']:
            self._reg['speed'] = new_speed
            self._push_value('moving_speed', new_speed)

    @property
    def torque_limit(self):
        return self._reg['torque']

    @torque_limit.setter
    def torque_limit(self, new_torque):
        if new_torque != self._reg['torque']:
            self._reg['torque'] = new_torque
            self._push_value('torque_limit', new_torque)

    @property
    def compliant(self):
        return self._reg['compliant']

    @compliant.setter
    def compliant(self, new_compliancy):
        if new_compliancy != self._reg['compliant']:
            self._reg['compliant'] = new_compliancy
            self._push_value('compliant', new_compliancy)

    def _update(self, new_state):
        if 'position' in new_state:
            new_pos = new_state['position']

            if new_pos != self._pos:
                self._pub_event('moved', self._pos, new_pos)
                self._pos = new_pos

        if 'speed' in new_state:
            new_speed = new_state['speed']

            if new_speed != self._speed:
                self._speed = new_speed

    def _state_repr(self):
        state = ''
        if self._pos is not None:
            state += 'position={}'.format(self._pos)
        if self._speed is not None:
            state += ' speed={}'.format(self._speed)
        return state
