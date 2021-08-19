from .service import Service


class Light(Service):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Light', id, alias, device)
        self._value = 0.0

    @property
    def lux(self):
        """ Light in lux. """
        return self._value

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'lux' in new_state:
            new_light = new_state['lux']
            if new_light != self._value:
                self._pub_event('changed', self._value, new_light)

                if abs(new_light - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_light)

                self._value = new_light
