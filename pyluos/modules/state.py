from .module import Module


class State(Module):
    possible_events = {'changed', 'falling', 'rising'}

    def __init__(self, id, alias, device):
        Module.__init__(self, 'State', id, alias, device)
        self._value = False

    @property
    def state(self):
        return self._value == True

    @state.setter
    def state(self, new_val):
        self._value == new_val
        self._push_value('io_state', new_val)

    def _update(self, new_state):
        Module._update(self, new_state)
        if 'io_state' in new_state:
            new_state = new_state['io_state']
            if new_state != self._value:
                self._pub_event('changed', self._value, new_state)

                evt = 'pressed' if new_state == True else 'released'
                self._pub_event(evt, self._value, new_state)

                self._value = new_state

    def control(self):
        def switch(state):
            self.state = state

        return interact(switch, state=self._value)
