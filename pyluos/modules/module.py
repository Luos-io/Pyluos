from collections import defaultdict, namedtuple

import logging

logger = logging.getLogger(__name__)

try:
    from ipywidget import interact
except ImportError:
    def interact(*args, **kwargs):
        logger.warning('You first have to install ipywidgets to use the control widgets.')
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
        pass

    def _push_value(self, key, new_val):
        self._delegate.update_cmd(self.alias, key, new_val)

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
