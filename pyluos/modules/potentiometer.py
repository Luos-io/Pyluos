from .module import Module


class Potentiometer(Module):
    possible_events = {'moved'}

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Potentiometer', id, alias, robot)
        self._value = 0

    @property
    def position(self):
        """ Position in degrees. """
        return self._value

    def _update(self, new_state):
        Module._update(self, new_state)
        new_pos = new_state['position']

        if new_pos != self._value:
            self._value = new_pos
            self._pub_event('moved', self._value, self.position)
