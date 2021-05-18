from .container import Container


class Gate(Container):

    def __init__(self, id, alias, device):
        Container.__init__(self, 'Gate', id, alias, device)

    def _update(self, new_state):
        Container._update(self, new_state)

    def control(self):
        def delay(delay):
            self._value = delay

        return interact(delay, delay=(0, 100, 1))
