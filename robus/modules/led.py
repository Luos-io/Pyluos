from .module import Module


class Led(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'LED', id, alias, robot)
        self.color = (0, 0, 0)

    @property
    def color(self):
        return self._value

    @color.setter
    def color(self, new_color):
        if new_color != self._value:
            self._value = new_color
            self._push_value(new_color)
