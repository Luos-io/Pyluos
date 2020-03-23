from .module import Module


class Voltage(Module):
    possible_events = {'changed', 'filter_changed'}

    def __init__(self, id, alias, device):
        Module.__init__(self, 'Voltage', id, alias, device)
        self._value = 0
        self.threshold = 1.0

    @property
    def volt(self):
        """ Voltage in volt. """
        return self._value

    @volt.setter
    def volt(self, new_val):
        self._value = new_val
        self._push_value('volt', new_val)

    def _update(self, new_state):
        Module._update(self, new_state)
        if 'volt' in new_state:
            new_val = new_state['volt']
            if new_val != self._value:
                self._pub_event('changed', self._value, new_val)
                if abs(new_val - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_val)
            self._value = new_val

    def control(self):
        def move(val):
            self._value = val

        return interact(move, val=(0.0, 3.3, 0.1))
