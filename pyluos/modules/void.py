from .module import Module


class Void(Module):

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Void', id, alias, robot)
        self._baudrate = 1000000

    def _update(self, new_state):
        Module._update(self, new_state)

    def dxl_detect(self):
        self._push_value('reinit', 0)

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, baud):
        new_val = [4, baud]
        self._push_value('register', new_val)
        self._baudrate = baud
