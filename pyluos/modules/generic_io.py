from .module import Module, interact


class L0GenericIO(Module):
    def __init__(self, id, alias, robot):
        Module.__init__(self, 'L0GenericIO', id, alias, robot)

        # Input Pins
        self._p1 = None
        self._p8 = 0
        self._p9 = None
        self._p10 = None
        self._p11 = None
        self._p12 = None

        # Output Pins
        self._p2 = None
        self._p3 = None
        self._p4 = None

    @property
    def p1(self):
        return self._p1

    @property
    def p8(self):
        return self._p8

    @property
    def p9(self):
        return self._p9

    @property
    def p10(self):
        return self._p10

    @property
    def p11(self):
        return self._p11

    @property
    def p12(self):
        return self._p12

    def _update(self, new_state):
        self._p1 = new_state['p1']
        self._p8 = new_state['p8']
        self._p9 = new_state['p9']
        self._p10 = new_state['p10']
        self._p11 = new_state['p11']
        self._p12 = new_state['p12']

    @property
    def p2(self):
        return self._p2

    @p2.setter
    def p2(self, new_val):
        if new_val != self._p2:
            self._p2 = new_val
            self._push_value('p2', self._p2)

    @property
    def p3(self):
        return self._p3

    @p3.setter
    def p3(self, new_val):
        if new_val != self._p3:
            self._p3 = new_val
            self._push_value('p3', self._p3)

    @property
    def p4(self):
        return self._p4

    @p4.setter
    def p4(self, new_val):
        if new_val != self._p4:
            self._p4 = new_val
            self._push_value('p4', self._p4)

    def control(self):
        def change_pin(p2, p3, p4):
            self.p2 = p2
            self.p3 = p3
            self.p4 = p4

        return interact(change_pin, p2=self.p2, p3=self.p3, p4=self.p4)
