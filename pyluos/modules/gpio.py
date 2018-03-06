class DigitalInputPin(object):
    def __init__(self, alias, default=False):
        self.alias = alias
        self._val = default

    def is_high(self):
        return self._val

    def is_low(self):
        return not self.is_high()

    def _update(self, val):
        self._val = (val == 1)

    def __repr__(self):
        return '<"{}" Input state="{}">'.format(
            self.alias,
            'high' if self.is_high() else 'low'
        )


class AnalogInputPin(object):
    def __init__(self, alias, default=0):
        self.alias = alias
        self._val = default

    def read(self):
        return self._val

    def _update(self, val):
        self._val = val

    def __repr__(self):
        return '<"{}" Input value="{}">'.format(
            self.alias,
            self.read()
        )


class DigitalOutputPin(object):
    def __init__(self, alias, delegate, default=False):
        self.alias = alias
        self._delegate = delegate
        self._val = default

    def is_high(self):
        return self._val

    def set_high(self):
        self._push(True)

    def is_low(self):
        return not self.is_high()

    def set_low(self):
        self._push(False)

    def toggle(self):
        if self.is_high():
            self.set_low()
        else:
            self.set_high()

    def _push(self, val):
        if self._val != val:
            self._val = val
            self._delegate._push_value(self.alias, self._val)

    def __repr__(self):
        return '<"{}" Output state="{}">'.format(
            self.alias,
            'high' if self.is_high() else 'low'
        )


class Pwm(object):
    def __init__(self, alias, delegate, default=0.0, min=0.0, max=1.0):
        self.alias = alias
        self._delegate = delegate
        self._val = default
        self._min, self._max = min, max

    @property
    def duty_cycle(self):
        return self._val

    @duty_cycle.setter
    def duty_cycle(self, duty):
        self._push(min(max(duty, self._min), self._max))

    def _push(self, val):
        if self._val != val:
            self._val = val
            self._delegate._push_value(self.alias, self._val)
