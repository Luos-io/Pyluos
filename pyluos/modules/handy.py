from .module import Module, interact

class Handy(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Handy', id, alias, robot)

        self.fingers = {'index': 0.0, 'middle': 0.0, 'ring': 0.0, 'pinky': 0.0, 'thumb': 0.0, }

    def power_ratio(self, s, name):
        s = min(max(s, 0.0), 100.0)

        if s != self.fingers[name]:
            self.fingers[name] = s
            self._push_value(name,s)

    @property
    def index(self):
        return self.fingers["index"]

    @index.setter
    def index(self, s):
        self.power_ratio(s,"index")

    @property
    def middle(self):
        return self.fingers["middle"]

    @middle.setter
    def middle(self, s):
        self.power_ratio(s,"middle")

    @property
    def ring(self):
        return self.fingers["ring"]

    @ring.setter
    def ring(self, s):
        self.power_ratio(s,"ring")

    @property
    def pinky(self):
        return self.fingers["pinky"]

    @pinky.setter
    def pinky(self, s):
        self.power_ratio(s,"pinky")

    @property
    def thumb(self):
        return self.fingers["thumb"]

    @thumb.setter
    def thumb(self, s):
        self.power_ratio(s,"thumb")

    def control(self):
        def change_pos(index, middle, ring, pinky, thumb):
            self.index = index
            self.middle = middle
            self.ring = ring
            self.pinky = pinky
            self.thumb = thumb

        return interact(change_pos,
                        index=lambda: self.m1.target_position,
                        middle=lambda: self.m2.target_position,
                        ring=lambda: self.m3.target_position,
                        pinky=lambda: self.m4.target_position,
                        thumb=lambda: self.m5.target_position)
