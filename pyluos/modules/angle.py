from .module import Module


class Angle(Module):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Module.__init__(self, 'Angle', id, alias, device)
        self._value = 0

    @property
    def rot_position(self):
        """ Position in degrees. """
        return self._value

    def _update(self, new_state):
        Module._update(self, new_state)
        if 'rot_position' in new_state:
            new_val = new_state['rot_position']
            if new_val != self._value:
                self._pub_event('changed', self._value, new_val)

                if abs(new_val - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_val)

                self._value = new_val
