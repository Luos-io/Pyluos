import os
import sys
import json
import time
import logging
import threading
import logging.config
import numpy as np

from datetime import datetime
from collections import defaultdict

from .io import discover_hosts, io_from_host, Ws
from .modules import name2mod

from anytree import AnyNode, RenderTree


def run_from_unittest():
    return 'unittest' in sys.modules


known_host = {
    'ergo': ['/dev/cu.usbserial-DN2AAOVK', '/dev/cu.usbserial-DN2YEFLN'],
    'handy': ['/dev/cu.usbserial-DN2X236E'],
    'eddy': ['pi-gate.local'],
}


class moduList(list):
    def __repr__(self):
        s = '-------------------------------------------------\n'
        s += '{:<20s}{:<20s}{:<5s}\n'.format("Type", "Alias", "ID")
        s += '-------------------------------------------------\n'
        for elem in self:
            s += '{:<20s}{:<20s}{:<5d}\n'.format(elem.type, elem.alias, elem.id)
        return s

class nodeList(list):
    def __repr__(self):
        # Display the topology
        s = ''
        for pre, fill, node in RenderTree(self[0]):
            if (node.parent == None):
                branch = " root : "
            else:
                l_port_id = [i for i,x in enumerate(node.parent.port_table) if x == node.modules[0].id]
                r_port_id = node.port_table.index(min(node.port_table))
                branch = str(l_port_id[0]) + "<=>" + str(r_port_id) + " : "
            s += "%s%s%s\n" % (pre, branch, node.id)
            s += fill + "        |  " + '{:<20s}{:<20s}{:<5s}\n'.format("Type", "Alias", "ID")
            for y,elem in enumerate(node.modules):
                s += fill + "        └> " + '{:<20s}{:<20s}{:<5d}\n'.format(elem.type, elem.alias, elem.id)
        return s

class Device(object):
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
        self.logger.info('Device setup.')

        self._last_update = time.time()
        self._running = True
        self._pause = False

        # Setup both poll/push synchronization loops.
        self._poll_bg = threading.Thread(target=self._poll_and_up)
        self._poll_bg.daemon = True
        self._poll_bg.start()
        self._baudrate = 1000000

    def close(self):
        self._running = False
        self._poll_bg.join()
        self._io.close()

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, baudrate):
        self._send({'baudrate': baudrate})
        self._baudrate = baudrate
        time.sleep(0.01)

    def benchmark(self, target_id, data, repetition):
        data = np.array(data, dtype=np.uint8)
        self._bench_settings = {'benchmark': {'target': target_id, 'repetitions': repetition, 'data': [len(data)]}}
        self._bench_Data = data.tobytes()
        self._write( json.dumps(self._bench_settings).encode() + '\r'.encode() + self._bench_Data)

        state = self._poll_once()
        while ('benchmark' not in state):
            state = self._poll_once()

        #self._pause = False
        return (state['benchmark']['data_rate'], state['benchmark']['fail_rate'])

    def pause(self):
        self._pause = True
        time.sleep(1)

    def play(self):
        self._pause = False

    def _setup(self):
        self.logger.info('Sending detection signal.')
        self._send({'detection': {}})
        self.logger.info('Waiting for route table...')

        startTime = time.time()
        state = self._poll_once()
        while ('route_table' not in state):
            state = self._poll_once()
            if (time.time()-startTime > 1):
                self._send({'detection': {}})
                startTime = time.time()

        # Create nodes
        self._modules = []
        self._nodes = []
        for i, node in enumerate(state['route_table']):
            parent_elem = None
            # find a parent and create a link
            if (min(node["port_table"]) < node["modules"][0]["id"]):
                parent_id = min(node["port_table"])
                for elem in self._nodes:
                    for module in elem.modules:
                        if (module.id == parent_id):
                            parent_elem = elem
                            break;
            # create the node
            self._nodes.append(AnyNode(id=node["uuid"], parent=parent_elem, port_table=node["port_table"]))

            filtered_modules = moduList([mod for mod in node["modules"]
                                if 'type' in mod and mod['type'] in name2mod.keys()])
            # Create a list of modules in the node
            self._nodes[i].modules = [
                name2mod[mod['type']](id=mod['id'],
                                      alias=mod['alias'],
                                      device=self)
                for mod in filtered_modules
                if 'type' in mod and 'id' in mod and 'alias' in mod
            ]
            # Create a list of modules of the entire device
            self._modules = self._modules + self._nodes[i].modules
            for mod in self._nodes[i].modules:
                setattr(self, mod.alias, mod)

        self._cmd = defaultdict(lambda: defaultdict(lambda: None))
        self._cmd_data = []
        self._binary = []

        # We push our current state to make sure that
        # both our model and the hardware are synced.
        self._push_once()

    @property
    def modules(self):
        return moduList(self._modules)

    @property
    def nodes(self):
        return nodeList(self._nodes)

    # Poll state from hardware.
    def _poll_once(self):
        self._state = self._io.read()
        self._state['timestamp'] = time.time()
        return self._state

    def _poll_and_up(self):
        while self._running:
            if not self._pause :
                state = self._poll_once()
                self._update(state)
                self._push_once()
            else :
                time.sleep(0.1)

    # Update our model with the new state.
    def _update(self, new_state):
        if 'dead_module' in new_state :
            #we have lost a module put a flag on this module
            alias = new_state['dead_module']
            if hasattr(self, alias):
                getattr(self, alias)._kill()
        if 'modules' not in new_state:
            return

        for alias, mod in new_state['modules'].items():
            if hasattr(self, alias):
                getattr(self, alias)._update(mod)

        self._last_update = time.time()

    def update_cmd(self, alias, key, val):
        with self._cmd_lock:
            self._cmd[alias][key] = val

    def update_data(self, alias, key, val, data):
        with self._cmd_lock:
            self._cmd_data.append({alias: {key: val}})
            self._binary.append(data.tobytes())

    def _push_once(self):
        with self._cmd_lock:
            if self._cmd:
                self._write( json.dumps({'modules': self._cmd}).encode())
                self._cmd = defaultdict(lambda: defaultdict(lambda: None))
            for cmd, binary in zip(self._cmd_data, self._binary):
                time.sleep(0.01)
                self._write( json.dumps({'modules': cmd}).encode() + '\r'.encode() + binary)

            self._cmd_data = []
            self._binary = []


    def _send(self, msg):
        with self._send_lock:
            self._io.send(msg)

    def _write(self, data):
        with self._send_lock:
            self._io.write(data)
