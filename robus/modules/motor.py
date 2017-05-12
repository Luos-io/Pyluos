from .module import Module


class Motor(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Motor', id, alias, robot)
        self.position = 90

    @property
    def position(self):
        return self._value

    @position.setter
    def position(self, new_pos):
        if new_pos != self._value:
            self._value = new_pos
            self._push_value(new_pos)
