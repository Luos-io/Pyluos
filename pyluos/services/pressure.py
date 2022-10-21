from .service import Service


class Pressure(Service):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Pressure', id, alias, device)
        self._value = 0

    @property
    def pressure(self):
        """ Pressure in Pa. """
        return self._value

    @pressure.setter
    def pressure(self, new_val):
        self._value = new_val
        self._push_value('pressure', new_val)

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'pressure' in new_state.keys():
            new_val = new_state['pressure']
            if new_val != self._value:
                self._pub_event('changed', self._value, new_val)

                if abs(new_val - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_val)

                self._value = new_val
