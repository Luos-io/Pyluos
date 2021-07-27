from .service import Service, interact


class PowerSwitch(Service):
    def __init__(self, id, alias, device):
        Service.__init__(self, 'PowerSwitch', id, alias, device)
        self._value = False

    @property
    def state(self):
        self._value

    @state.setter
    def state(self, s):
        self._value = s
        self._push_value("io_state",s)

    def _update(self, new_state):
        Service._update(self, new_state)

    def control(self):
        def switch(state):
            self.state = state

        return interact(switch, state=self._value)
