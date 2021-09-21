from .service import Service


class Distance(Service):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, device):
        Service.__init__(self, 'Distance', id, alias, device)
        self._value = 0

    @property
    def distance(self):
        """ Distance in mm. """
        return self._value

    def _update(self, new_state):
        Service._update(self, new_state)
        if 'trans_position' in new_state:
            new_dist = new_state['trans_position']
            if new_dist != self._value:
                self._pub_event('changed', self._value, new_dist)

                if abs(new_dist - self._value) > self.threshold:
                    self._pub_event('filter_changed',
                                    self._value, new_dist)

                self._value = new_dist
