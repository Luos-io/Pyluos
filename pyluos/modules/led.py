from .module import Module, interact


class Led(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'LED', id, alias, robot)
        self.color = (0, 0, 0)
        self.time = 0.0

    @property
    def color(self):
        return self._value

    @color.setter
    def color(self, new_color):
        new_color = [int(min(max(c, 0), 255)) for c in new_color]
        self._value = new_color
        self._push_value('color', new_color)

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        self._time = new_time
        self._push_value('time', new_time)

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def change_color(red, green, blue):
            self.color = (red, green, blue)

        return interact(change_color,
                        red=(0, 255, 1),
                        green=(0, 255, 1),
                        blue=(0, 255, 1))
