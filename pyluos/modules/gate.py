from .module import Module


class Gate(Module):

    def __init__(self, id, alias, device):
        Module.__init__(self, 'Gate', id, alias, device)

    def _update(self, new_state):
        Module._update(self, new_state)

    @property
    def delay_ms(self):
        self._value

    @delay_ms.setter
    def delay_ms(self, s):
        self._value = s
        self._push_value("delay",s)

    def control(self):
        def delay(delay):
            self._value = delay

        return interact(delay, delay=(0, 100, 1))
