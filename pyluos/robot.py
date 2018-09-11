import os
import sys
import json
import time
import logging
import threading
import logging.config

from datetime import datetime
from collections import defaultdict

from .io import discover_hosts, io_from_host, Ws
from .modules import name2mod


def run_from_unittest():
    return 'unittest' in sys.modules


use_topographe = True
try:
    import zmq
except ImportError:
    use_topographe = False


known_host = {
    'ergo': ['/dev/cu.usbserial-DN2AAOVK', '/dev/cu.usbserial-DN2YEFLN'],
    'handy': ['/dev/cu.usbserial-DN2X236E'],
    'eddy': ['pi-gate.local'],
}


class Robot(object):
    _heartbeat_timeout = 5  # in sec.
    _max_alias_length = 15
    _base_log_conf = os.path.join(os.path.dirname(__file__),
                                  'logging_conf.json')

    @classmethod
    def discover(cls):
        hosts = discover_hosts()

        possibilities = {
            k: [h for h in v if h in hosts]
            for k, v in known_host.items()
        }

        return possibilities

    def __init__(self, host,
                 IO=None,
                 log_conf=_base_log_conf,
                 test_mode=False,
                 *args, **kwargs):
        if IO is not None:
            self._io = IO(host=host, *args, **kwargs)
        else:
            self._io = io_from_host(host=host,
                                    *args, **kwargs)

        if os.path.exists(log_conf):
            with open(log_conf) as f:
                config = json.load(f)
            logging.config.dictConfig(config)

        self.logger = logging.getLogger(__name__)
        self.logger.info('Connected to "{}".'.format(host))

        self._send_lock = threading.Lock()
        self._cmd_lock = threading.Lock()

        # We force a first poll to setup our model.
        self._setup()
        self.logger.info('Robot setup.')

        self._last_update = time.time()
        self._running = True

        # Setup both poll/push synchronization loops.
        self._poll_bg = threading.Thread(target=self._poll_and_up)
        self._poll_bg.daemon = True
        self._poll_bg.start()

        if not (test_mode or run_from_unittest()) and use_topographe:
            c = zmq.Context()
            s = c.socket(zmq.PUB)
            s.connect('tcp://127.0.0.1:33000')
            self._s = s

    @property
    def state(self):
        return {
            'gate': self.name,
            'timestamp': datetime.now(),
            'types': ','.join([mod.type for mod in self.modules]),
            'modules': ','.join([mod.alias for mod in self.modules])
        }

    @property
    def name(self):
        return self._name

    @property
    def alive(self):
        dt = time.time() - self._last_update
        return self._running and dt < self._heartbeat_timeout

    def close(self):
        self._running = False
        self._poll_bg.join()
        self._io.close()

    def _setup(self):
        self.logger.info('Sending detection signal.')
        self._send({'detection': {}})
        if isinstance(self._io, Ws):
            import time
            time.sleep(0.1)
            self._send({'detection': {}})

        self.logger.info('Waiting for first state...')
        #while not self._io.is_ready():
        #self._send({'detection': {}})

        state = self._poll_once()

        try:
            gate = next(g for g in state['modules']
                        if 'type' in g and g['type'] == 'gate')
            self._name = gate['alias']
        except StopIteration:
            self._name = 'gate_unknown'

        modules = [mod for mod in state['modules']
                   if 'type' in mod and mod['type'] in name2mod.keys()]

        self._cmd = defaultdict(lambda: defaultdict(lambda: None))

        self.modules = [
            name2mod[mod['type']](id=mod['id'],
                                  alias=mod['alias'],
                                  robot=self)
            for mod in modules
            if 'type' in mod and 'id' in mod and 'alias' in mod
        ]

        for mod in self.modules:
            setattr(self, mod.alias, mod)

        # We push our current state to make sure that
        # both our model and the hardware are synced.
        self._push_once()

    # Poll state from hardware.
    def _poll_once(self):
        self._state = self._io.read()
        self._state['timestamp'] = time.time()
        return self._state

    def _poll_and_up(self):
        while self._running:
            state = self._poll_once()
            self._update(state)
            self._push_once()

            self._broadcast(state)

    # Update our model with the new state.
    def _update(self, new_state):
        if 'modules' not in new_state:
            return

        mod_need_update = [mod for mod in new_state['modules']
                           if hasattr(self, mod['alias']) and
                           set(mod.keys()) != {'type', 'id', 'alias'}]

        for mod in mod_need_update:
            getattr(self, mod['alias'])._update(mod)

        self._last_update = time.time()

    def update_cmd(self, alias, key, val):
        with self._cmd_lock:
            self._cmd[alias][key] = val

    def _push_once(self):
        with self._cmd_lock:
            if not self._cmd:
                return

            self._send({
                'modules': self._cmd
            })

            self._cmd = defaultdict(lambda: defaultdict(lambda: None))

    def _send(self, msg):
        with self._send_lock:
            self._io.send(msg)

    def _broadcast(self, state):
        if not hasattr(self, '_s'):
            return

        for mod in state['modules']:
            if ((mod['type'] == 'servo') and
               (hasattr(self, mod['alias']))):
                servo = getattr(self, mod['alias'])
                mod['position'] = servo.target_position

        msg = '{} {}'.format(self.name, json.dumps(state))
        self._s.send_string(msg)

    def rename_module(self, old, new):
        if not hasattr(self, old):
            raise ValueError('No module named {}!'.format(old))

        if len(new) > self._max_alias_length:
            raise ValueError(
                'Alias length should be less than {}'
                .format(self._max_alias_length)
            )

        self._send({'modules': {old: {'set_alias': new}}})

        mod = getattr(self, old)
        mod.alias = new
        setattr(self, new, mod)
        delattr(self, old)
