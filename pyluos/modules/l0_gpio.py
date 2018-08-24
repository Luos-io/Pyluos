from .module import Module, interact
from .gpio import AnalogInputPin, DigitalInputPin, DigitalOutputPin, Pwm


class GPIO(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'GPIO', id, alias, robot)

        self.analog_1 = AnalogInputPin('p1')

        self.digital_2 = DigitalOutputPin('p2', self)
        self.digital_3 = DigitalOutputPin('p3', self)
        self.digital_4 = DigitalOutputPin('p4', self)

        self.digital_5 = DigitalInputPin('p5')
        self.digital_6 = DigitalInputPin('p6')
        self.analog_7 = AnalogInputPin('p7')
        self.analog_8 = AnalogInputPin('p8')
        self.analog_9 = AnalogInputPin('p9')

    def _update(self, new_state):
        Module._update(self, new_state)

        if 'p1' in new_state:
            self.analog_1._update(new_state['p1'])
            self.digital_5._update(new_state['p5'])
            self.digital_6._update(new_state['p6'])
            self.analog_7._update(new_state['p7'])
            self.analog_8._update(new_state['p8'])
            self.analog_9._update(new_state['p9'])

    # notebook things
    def control(self):
        def change_pin(p2, p3, p4):
            self.digital_2._push(p2)
            self.digital_3._push(p3)
            self.digital_4._push(p4)

        return interact(change_pin,
                        p2=self.digital_2.is_high(),
                        p3=self.digital_3.is_high(),
                        p4=self.digital_4.is_high())
