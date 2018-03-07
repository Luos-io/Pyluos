from .module import Module, interact
from .gpio import Pwm


class L0Servo(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0Servo', id, alias, robot)

        self.pwm_1 = Pwm('p1', self, max=180.0)
        self.pwm_2 = Pwm('p2', self, max=180.0)
        self.pwm_3 = Pwm('p3', self, max=180.0)
        self.pwm_4 = Pwm('p4', self, max=180.0)

    def control(self):
        def change_pin(p1, p2, p3, p4):
            self.p1._push(p1)
            self.p2._push(p2)
            self.p3._push(p3)
            self.p4._push(p4)

        return interact(change_pin,
                        p1=lambda: self.pwm_1.duty_cycle,
                        p2=lambda: self.pwm_2.duty_cycle,
                        p3=lambda: self.pwm_3.duty_cycle,
                        p4=lambda: self.pwm_4.duty_cycle)
