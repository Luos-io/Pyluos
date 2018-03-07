from .module import Module, interact
from .gpio import AnalogInputPin, DigitalInputPin, DigitalOutputPin, Pwm


class L0GPIO(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0GPIO', id, alias, robot)

        self.pwm_1 = Pwm('p1', self)
        self.pwm_2 = Pwm('p2', self)
        self.digital_3 = DigitalOutputPin('p3', self)
        self.digital_4 = DigitalOutputPin('p4', self)

        self.digital_5 = DigitalInputPin('p5')
        self.digital_6 = DigitalInputPin('p6')
        self.analog_7 = AnalogInputPin('p7')
        self.analog_8 = AnalogInputPin('p8')
        self.analog_9 = AnalogInputPin('p9')

    def _update(self, new_state):
        self.digital_5._update(new_state['p5'])
        self.digital_6._update(new_state['p6'])
        self.analog_7._update(new_state['p7'])
        self.analog_8._update(new_state['p8'])
        self.analog_9._update(new_state['p9'])

    def control(self):
        def change_pin(p1, p2, p3, p4):
            self.p1._push(p1)
            self.p2._push(p2)
            self.p3._push(p3)
            self.p4._push(p4)

        return interact(change_pin,
                        p1=lambda: self.pwm_1.duty_cycle,
                        p2=lambda: self.pwm_2.duty_cycle,
                        p3=self.digital_3.is_high(),
                        p4=self.digital_4.is_high())
