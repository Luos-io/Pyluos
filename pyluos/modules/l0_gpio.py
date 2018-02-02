from .module import Module, interact
from .gpio import AnalogInputPin, DigitalInputPin, DigitalOutputPin


class L0GPIO(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0GPIO', id, alias, robot)

        # Input Pins
        self.p1 = AnalogInputPin('p1')
        self.p8 = DigitalInputPin('p8')
        self.p9 = DigitalInputPin('p9')
        self.p10 = DigitalInputPin('p10')
        self.p11 = DigitalInputPin('p11')
        self.p12 = AnalogInputPin('p12')

        # Output Pins
        self.p2 = DigitalOutputPin('p2', self)
        self.p3 = DigitalOutputPin('p3', self)
        self.p4 = DigitalOutputPin('p4', self)

        self.pins = {
            'p1': self.p1,
            'p2': self.p2,
            'p3': self.p3,
            'p4': self.p4,
            'p8': self.p8,
            'p9': self.p9,
            'p10': self.p10,
            'p11': self.p11,
            'p12': self.p12,
        }

    def __repr__(self):
        return '<"{}": {}>'.format(
            self.alias,
            str(list(self.pins.values())),
        )

    def _update(self, new_state):
        self.p1._update(new_state['p1'])
        self.p8._update(new_state['p8'])
        self.p9._update(new_state['p9'])
        self.p10._update(new_state['p10'])
        self.p11._update(new_state['p11'])
        self.p12._update(new_state['p12'])

    def control(self):
        def change_pin(p2, p3, p4):
            self.p2._push(p2)
            self.p3._push(p3)
            self.p4._push(p4)

        return interact(change_pin,
                        p2=self.p2.is_high(),
                        p3=self.p3.is_high(),
                        p4=self.p4.is_high())
