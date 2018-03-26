from .module import Module, interact
from .gpio import Pwm


class PositionServo(object):
    def __init__(self, alias, delegate, default=0.0, min=0.0, max=180.0):
        self._pos = None
        self._pwm = Pwm(alias, delegate, default, min, max)

    @property
    def target_position(self):
        return self._pos

    @target_position.setter
    def target_position(self, pos):
        if pos != self._pos:
            self._pwm.duty_cycle = pos
            self._pos = pos


class L0Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0Servo', id, alias, robot)

        self.m1 = PositionServo('p1', self)
        self.m2 = PositionServo('p2', self)
        self.m3 = PositionServo('p3', self)
        self.m4 = PositionServo('p4', self)

    def control(self):
        def change_pos(p1, p2, p3, p4):
            self.m1.target_position = p1
            self.m2.target_position = p2
            self.m3.target_position = p3
            self.m4.target_position = p4

        return interact(change_pos,
                        p1=lambda: self.m1.target_position,
                        p2=lambda: self.m2.target_position,
                        p3=lambda: self.m3.target_position,
                        p4=lambda: self.m4.target_position)
