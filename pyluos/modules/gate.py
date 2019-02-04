from .module import Module


class Gate(Module):

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Gate', id, alias, robot)

    def _update(self, new_state):
        Module._update(self, new_state)
