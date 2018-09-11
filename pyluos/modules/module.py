from collections import defaultdict, namedtuple

import logging
import time

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
        self._firmware_revision = "Unknown"

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
        if 'revision' in new_state:
            self._firmware_revision = new_state['revision']

    def _push_value(self, key, new_val):
        self._delegate.update_cmd(self.alias, key, new_val)

    @property
    def L0_temperature(self):
        self._push_value('L0_temperature', "")
        time.sleep(0.1)
        return self._L0_temperature

    @property
    def L0_voltage(self):
        self._push_value('L0_voltage', "")
        time.sleep(0.1)
        return self._L0_voltage

    @property
    def firmware_revision(self):
        self._push_value('revision', "")
        time.sleep(0.1)
        return self._firmware_revision

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

    def rename(self, name):
        # check if the string start with a number before sending
        self._push_value('rename', name)
        self.alias = name
        print("You should restart your network to avoid name propagation fault.")


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
