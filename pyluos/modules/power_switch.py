from .module import Module, interact


class PowerSwitch(Module):
    def __init__(self, id, alias, device):
        Module.__init__(self, 'PowerSwitch', id, alias, device)
        self._value = False

    @property
    def state(self):
        self._value

    @state.setter
    def state(self, s):
        self._value = s
        self._push_value("io_state",s)

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def switch(state):
            self.state = state

        return interact(switch, state=self._value)
