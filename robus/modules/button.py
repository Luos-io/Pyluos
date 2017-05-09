from .module import Module, Event


class Button(Module):
    possible_events = {'changed', 'pressed', 'released'}

    def __init__(self, id, alias):
        Module.__init__(self, 'Button', id, alias)
        self._value = 'OFF'

    @property
    def state(self):
        return self._value

    def _update(self, new_state):
        events = []
        new_state = 'ON' if new_state['value'] else 'OFF'

        if new_state != self._value:
            events.append(Event('changed', self._value, new_state))
            e = Event('pressed' if new_state == 'ON' else 'released',
                      self._value, new_state)
            events.append(e)
            self._value = new_state

        self._pub_events(events)
