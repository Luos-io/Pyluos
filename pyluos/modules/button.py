from .module import Module


class Button(Module):
    possible_events = {'changed', 'pressed', 'released'}

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Button', id, alias, robot)
        self._value = 'OFF'

    @property
    def pressed(self):
        return self._value == 'ON'

    def _update(self, new_state):
        Module._update(self, new_state)
        new_state = 'ON' if new_state['io_state'] else 'OFF'

        if new_state != self._value:
            self._pub_event('changed', self._value, new_state)

            evt = 'pressed' if new_state == 'ON' else 'released'
            self._pub_event(evt, self._value, new_state)

            self._value = new_state
