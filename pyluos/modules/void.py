from .module import Module


class Void(Module):

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Void', id, alias, robot)

    def _update(self, new_state):
        Module._update(self, new_state)

    def dxl_detect(self):
        self._push_value('reinit', 0)
