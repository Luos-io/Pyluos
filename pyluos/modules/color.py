from .module import Module, interact
import numpy as np


class Color(Module):
    def __init__(self, id, alias, device):
        Module.__init__(self, 'Color', id, alias, device)
        self._time = None

    @property
    def color(self):
        return self._value

    @color.setter
    def color(self, new_color):
        new_color = [int(min(max(c, 0), 255)) for c in new_color]
        if len(new_color) > 3 :
            self._value = new_color
            self._push_data('color', [len(new_color)], np.array(new_color, dtype=np.uint8))
        else :
            self._value = new_color
            self._push_value('color', new_color)
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, new_time):
        self._time = new_time
        self._push_value('time', new_time)

    @property
    def size(self):
        return self._size

    @time.setter
    def size(self, new_size):
        self._size = new_size
        self._push_value('parameters', new_size)

    def _update(self, new_state):
        Module._update(self, new_state)

    def control(self):
        def change_color(red, green, blue):
            self.color = (red, green, blue)

        return interact(change_color,
                        red=(0, 255, 1),
                        green=(0, 255, 1),
                        blue=(0, 255, 1))
