class DigitalInputPin(object):
    def __init__(self, default=False):
        self._val = default

    def is_high(self):
        return self._val

    def is_low(self):
        return not self.is_high()

    def _update(self, val):
        self._val = (val == 1)

    def __repr__(self):
        return '<Digital-Input-Pin: state="{}">'.format(
            'high' if self.is_high() else 'low'
        )


class AnalogInputPin(object):
    def __init__(self, default=0):
        self._val = default

    def read(self):
        return self._val

    def _update(self, val):
        self._val = val

    def __repr__(self):
        return '<Analog-Input-Pin: value="{}">'.format(
            self.read()
        )


class DigitalOutputPin(object):
    def __init__(self, field, delegate, default=False):
        self._field = field
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
            self._delegate._push_value(self._field, self._val)

    def __repr__(self):
        return '<Digital-Output-Pin: state="{}">'.format(
            'high' if self.is_high() else 'low'
        )
