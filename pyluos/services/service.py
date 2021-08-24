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


class Service(object):
    possible_events = set()

    def __init__(self,
                 type, id, alias,
                 device):
        self.id = id
        self.type = type
        self.alias = alias
        self.refresh_freq = 0.0
        self._update_time = 0.01
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
        self._luos_statistics = {}

    def __repr__(self):
        return ('<{self.type} '
                'alias="{self.alias}" '
                'id={self.id}>'.format(self=self))

    def _update(self, new_state):
        if ((time.time() - self._last_update) != 0):
            self.refresh_freq = ((200.0 * self.refresh_freq) + (1.0 / (time.time() - self._last_update))) / 201.0
            self._last_update = time.time()
        if 'revision' in new_state:
            self._firmware_revision = new_state['revision']
        if 'luos_revision' in new_state:
            self._luos_revision = new_state['luos_revision']
        if 'uuid' in new_state:
            self._uuid = new_state['uuid']
        if 'luos_statistics' in new_state:
            self._luos_statistics = new_state['luos_statistics']

    def _kill(self):
        self._killed = True
        print ("service", self.alias, "have been excluded from the network due to no responses.")

    def _push_value(self, key, new_val):
        if (self._killed) :
            print("service", self.alias,"is excluded.")
        else :
            if isinstance(new_val, float) :
                self._delegate.update_cmd(self.alias, key, float(str("%.3f" % new_val)))
            else :
                self._delegate.update_cmd(self.alias, key, new_val)

    def _push_data(self, key, new_val, data):
        if (self._killed) :
            print("service", self.alias,"is excluded.")
        else :
            self._delegate.update_data(self.alias, key, new_val, data)

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
    def uuid(self):
        self._push_value('uuid', "")
        time.sleep(0.03)
        return self._uuid

    @property
    def luos_statistics(self):
        self._push_value('luos_statistics', "")
        time.sleep(0.3)
        try:
            max_table = [self._luos_statistics["rx_msg_stack"], self._luos_statistics["luos_stack"], self._luos_statistics["tx_msg_stack"], self._luos_statistics["buffer_occupation"]]
            max_val = max(max_table)
            s = self.alias + " statistics :"
            s = s + "\n.luos allocated RAM occupation \t= " + repr(max_val)
            s = s + "%\n\t.RX message stack \t  = " + repr(self._luos_statistics["rx_msg_stack"])
            s = s + "%\n\t.TX message stack \t  = " + repr(self._luos_statistics["tx_msg_stack"])
            s = s + "%\n\t.Luos stack \t\t  = " + repr(self._luos_statistics["luos_stack"])
            s = s + "%\n\t.Buffer occupation \t  = " + repr(self._luos_statistics["buffer_occupation"])
            s = s + "%\n.Dropped messages number \t= " + repr(self._luos_statistics["msg_drop"])
            s = s + "\n.Max luos loop delay \t\t= " + repr(self._luos_statistics["loop_ms"])
            s = s + "ms\n.msg max retry number \t\t= " + repr(self._luos_statistics["max_retry"])
            s = s + "\n"
            print(s)
        except:
            print(self.alias + " statistics collection failed.\n")

    def rename(self, name):
        # check if the string start with a number before sending
        self._push_value('rename', name)
        self.alias = name

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, time):
        self._push_value('update_time', time)
        self._update_time= time

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
