from collections import defaultdict, namedtuple

import logging
import time

try:
    from ipywidgets import interact
    from ipywidgets import widgets
except ImportError:
    def interact(*args, **kwargs):
        msg = 'You first have to install ipywidgets to use the control widgets.'
        logging.getLogger(__name__).warning(msg)
        return None

    def widgets(*args, **kwargs):
        msg = 'You first have to install ipywidgets to use the control widgets.'
        logging.getLogger(__name__).warning(msg)
        return None

Event = namedtuple('Event', ('name', 'old_value', 'new_value'))


class Module(object):
    possible_events = set()

    def __init__(self,
                 type, id, alias,
                 device):
        self.id = id
        self.type = type
        self.alias = alias
        self.refresh_freq = 0.0
        self._delegate = device
        self._value = None
        self._cb = defaultdict(list)
        self._led = False
        self._node_temperature = None
        self._node_voltage = None
        self._firmware_revision = "Unknown"
        self._luos_revision = "Unknown"
        self._robus_revision = "Unknown"
        self._uuid = [0, 0, 0]
        self._killed = False
        self._last_update = time.time()

    def __repr__(self):
        return ('<{self.type} '
                'alias="{self.alias}" '
                'id={self.id}>'.format(self=self))

    def _update(self, new_state):
        if ((time.time() - self._last_update) != 0):
            self.refresh_freq = ((200.0 * self.refresh_freq) + (1.0 / (time.time() - self._last_update))) / 201.0
            self._last_update = time.time()
        if 'node_temperature' in new_state:
            self._node_temperature = new_state['node_temperature']
        if 'node_voltage' in new_state:
            self._node_voltage = new_state['node_voltage']
        if 'revision' in new_state:
            self._firmware_revision = new_state['revision']
        if 'luos_revision' in new_state:
            self._luos_revision = new_state['luos_revision']
        if 'robus_revision' in new_state:
            self._robus_revision = new_state['robus_revision']
        if 'uuid' in new_state:
            self._uuid = new_state['uuid']

    def _kill(self):
        self._killed = True
        print ("module", self.alias, "have been excluded from the network due to no responses.")

    def _push_value(self, key, new_val):
        if (self._killed) :
            print("module", self.alias,"is excluded.")
        else :
            if isinstance(new_val, float) :
                self._delegate.update_cmd(self.alias, key, float(str("%.3f" % new_val)))
            else :
                self._delegate.update_cmd(self.alias, key, new_val)

    def _push_data(self, key, new_val, data):
        if (self._killed) :
            print("module", self.alias,"is excluded.")
        else :
            self._delegate.update_data(self.alias, key, new_val, data)

    @property
    def node_temperature(self):
        self._push_value('node_temperature', "")
        time.sleep(0.03)
        return self._node_temperature

    @property
    def node_voltage(self):
        self._push_value('node_voltage', "")
        time.sleep(0.03)
        return self._node_voltage

    @property
    def firmware_revision(self):
        self._push_value('revision', "")
        time.sleep(0.03)
        return self._firmware_revision
        
    @property
    def luos_revision(self):
        self._push_value('luos_revision', "")
        time.sleep(0.03)
        return self._luos_revision
        
    @property
    def robus_revision(self):
        self._push_value('robus_revision', "")
        time.sleep(0.03)
        return self._robus_revision

    @property
    def uuid(self):
        self._push_value('uuid', "")
        time.sleep(0.03)
        return self._uuid

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
