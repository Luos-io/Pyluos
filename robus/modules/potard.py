from .module import Module, Event


class Potard(Module):
    possible_events = {'moved'}

    def __init__(self, id, alias):
        Module.__init__(self, 'Potard', id, alias)
        self._value = 0

    @property
    def position(self):
        return self._value

    def _update(self, new_state):
        new_pos = new_state['value']

        events = []
        if new_pos != self._value:
            events.append(Event('moved', self._value, new_pos))
            self._value = new_pos
        self._pub_events(events)
