from .module import Module


class Relay(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Relay', id, alias, robot)
        self.off()

    @property
    def state(self):
        return 'on' if self._value == 1 else 'off'

    def on(self):
        self._set(1)

    def off(self):
        self._set(0)

    def _set(self, new_val):
        if new_val != self._value:
            self._value = new_val
            self._push_value('state', new_val)
