from .service import Service


class Angle(Service):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Angle', id, alias, device)
        self._value = 0

    @property
    def rot_position(self):
        """ Position in degrees. """
        return self._value

    @rot_position.setter
    def rot_position(self, new_val):
        self._value = new_val
        self._push_value('target_rot_position', new_val)

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'rot_position' in new_state:
            new_val = new_state['rot_position']
            if new_val != self._value:
                self._pub_event('changed', self._value, new_val)

                if abs(new_val - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_val)

                self._value = new_val
