from .module import Module


class Distance(Module):
    possible_events = {'changed', 'filter_changed'}
    threshold = 10

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Distance', id, alias, robot)
        self._value = 0

    @property
    def distance(self):
        """ Distance in mm. """
        return self._value

    def _update(self, new_state):
        new_dist = new_state['distance']

        if new_dist != self._value:
            self._pub_event('changed', self._value, new_dist)

            if abs(new_dist - self._value) > self.threshold:
                self._pub_event('filter_changed',
                                self._value, new_dist)

            self._value = new_dist
