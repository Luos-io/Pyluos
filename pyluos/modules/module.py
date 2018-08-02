from collections import defaultdict, namedtuple

import logging


try:
    from ipywidgets import interact
except ImportError:
    def interact(*args, **kwargs):
        msg = 'You first have to install ipywidgets to use the control widgets.'
        logging.getLogger(__name__).warning(msg)
        return None


Event = namedtuple('Event', ('name', 'old_value', 'new_value'))


class Module(object):
    possible_events = set()

    def __init__(self,
                 type, id, alias,
                 robot):
        self.id = id
        self.type = type
        self.alias = alias
        self._delegate = robot
        self._value = None
        self._cb = defaultdict(list)
        self._led = True
        self._L0_temperature = None
        self._L0_voltage = None

    def __repr__(self):
        return ('<{self.type} '
                'alias="{self.alias}" '
                'id={self.id} '
                '{state}>'.format(self=self,
                                  state=self._state_repr()))

    def _state_repr(self):
        return ('state={}'.format(self._value)
                if self._value is not None else
                '')

    def _update(self, new_state):
        if 'L0_temperature' in new_state:
            self._L0_temperature = new_state['L0_temperature']
        if 'L0_voltage' in new_state:
            self._L0_voltage = new_state['L0_voltage']

    def _push_value(self, key, new_val):
        self._delegate.update_cmd(self.alias, key, new_val)

    @property
    def L0_temperature(self):
        self._push_value('L0_temperature', "")
        return self._L0_temperature

    @property
    def L0_voltage(self):
        self._push_value('L0_voltage', "")
        return self._L0_voltage

    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, state):
        if state != self._led:
            self._push_value('led', state)
            self._led = state

    def led_toggle(self):
        if self._led is True:
            self._push_value('led', False)
            self._led = False
        else:
            self._push_value('led', True)
            self._led = True

    # Events cb handling

    def add_callback(self, event, cb):
        if event not in self.possible_events:
            raise ValueError('Unknown callback: {} (poss={})'.format(event, self.possible_events))

        self._cb[event].append(cb)

    def remove_callback(self, event, cb):
        self._cb[event].remove(cb)

    def _pub_event(self, trigger, old_value, new_value):
        event = Event(trigger, old_value, new_value)

        for cb in self._cb[trigger]:
            cb(event)
