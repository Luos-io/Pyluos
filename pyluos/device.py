# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import uuid
import logging
import requests
import threading
import logging.config
import numpy as np

from datetime import datetime
from collections import defaultdict

from .io import discover_hosts, io_from_host, Ws
from .services import name2mod

from anytree import AnyNode, RenderTree, DoubleStyle


def run_from_unittest():
    return 'unittest' in sys.services

def map_custom_service(service_type, service_class):
    name2mod[service_type] = service_class

class contList(list):
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
        prefill = ''
        prechild = False
        for pre, fill, node in RenderTree(self[0], style=DoubleStyle()):
            # Draw the input part
            if (node.parent == None):
                branch = "  ┃  "
            else:
                branch = "═■┫  "

            # Draw the node body
            prefill = (prefill[:len(fill)]) if len(prefill) > len(fill) else prefill
            s += '{:<{fillsize}s}'.format(prefill, fillsize=len(fill))
            if (prechild == True):
                s = s[:-4] + '║' + s[-4 + 1:]
            s += '{:<54s}'.format("  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n")
            tmpstr = '{:<52s}'.format("%s╭────────────────── Node %s ──────────────────" % (branch, node.id))

            if (len(pre) > 0):
                pre = pre[:-1] + "═"
            s += pre + tmpstr + '{:>3s}'.format("┃\n")
            s += fill + "  ┃  │  " + '{:<20s}{:<20s}{:<4s}'.format("Type", "Alias", "ID") + '{:>3s}'.format("┃\n")
            for y, elem in enumerate(node.services):
                if (y == (len(node.services) - 1)):
                    s += fill + "  ┃  ╰> " + '{:<20s}{:<20s}{:<4d}'.format(elem.type, elem.alias, elem.id) + '{:>3s}'.format("┃\n")
                else:
                    s += fill + "  ┃  ├> " + '{:<20s}{:<20s}{:<4d}'.format(elem.type, elem.alias, elem.id) + '{:>3s}'.format("┃\n")

            # Draw the output part
            if (node.children):
                s += fill + "╔■┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                prechild = True
            else:
                s += fill + "  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n"
                prechild = False
            prefill = fill
        return s


class Device(object):
    _heartbeat_timeout = 5  # in sec.
    _max_alias_length = 15
    _base_log_conf = os.path.join(os.path.dirname(__file__),
                                  'logging_conf.json')
    _freedomLink = None

    def __init__(self, host,
                 IO=None,
                 log_conf=_base_log_conf,
                 test_mode=False,
                 background_task=True,
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

        if (background_task == True):
            # Setup both poll/push synchronization loops.
            self._poll_bg = threading.Thread(target=self._poll_and_up)
            self._poll_bg.daemon = True
            self._poll_bg.start()

    def close(self):
        self._running = False

        if hasattr(self, "_poll_bg"):
            self._poll_bg.join(timeout=2.0)

            if self._poll_bg.is_alive():
                # _poll_bg didn't terminate within the timeout
                print("Warning: device closed on timeout, background thread is still running.")
        self._io.close()

    def link_to_freedomrobotics(self):
        from .integration.freedomRobotics import FreedomLink
        self._freedomLink = FreedomLink(self)

    def pause(self):
        self._pause = True
        time.sleep(1)

    def play(self):
        self._pause = False

    def _setup(self):
        self.logger.info('Sending detection signal.')
        self._send({})
        time.sleep(0.01)
        self._send({'detection': {}})
        self.logger.info('Waiting for routing table...')
        startTime = time.time()
        state = self._poll_once()
        retry = 0
        while ('routing_table' not in state):
            if ('route_table' in state):
                self.logger.info("Watch out the Luos revision you are using on your board is too old to work with this revision of pyluos.\n Please consider updating Luos on your boards")
                return
            state = self._poll_once()
            if (time.time() - startTime > 5):
                retry = retry + 1
                if retry > 5:
                    # detection is not working
                    sys.exit("Detection failed.")
                self._send({'detection': {}})
                startTime = time.time()
        # Save routing table data
        self._routing_table = state
        # Create nodes
        self._services = []
        self._nodes = []
        for i, node in enumerate(state['routing_table']):
            if ('node_id' not in node):
                self.logger.info("Watch out the Luos revision you are using on your board is too old to work with this revision of pyluos.\n Please consider updating Luos on your boards")
            parent_elem = None
            # find a parent and create the link
            if (node["con"]["parent"][0] != 0):
                parent_id = node["con"]["parent"][0]
                for elem in self._nodes:
                    if (elem.id == parent_id):
                        parent_elem = elem
                        break
            # create the node
            self._nodes.append(AnyNode(id=node["node_id"], parent=parent_elem, connection=node["con"]))
            filtered_services = contList([mod for mod in node["services"]
                                          if 'type' in mod and mod['type'] in name2mod.keys()])
            # list unrecognized services and print a warning
            unrecognized_services = [mod for mod in node["services"]
                                        if 'type' in mod and mod['type'] not in name2mod.keys()]
            if (len(unrecognized_services) > 0):
                self.logger.warning("Unrecognized services have been detected on node %d" % node["node_id"])
                for mod in unrecognized_services:
                    self.logger.warning("  - service %s of type %s" % (mod['alias'], mod['type']))
            # Create a list of services in the node
            self._nodes[i].services = [
                name2mod[mod['type']](id=mod['id'],
                                      alias=mod['alias'],
                                      device=self)
                for mod in filtered_services
                if 'type' in mod and 'id' in mod and 'alias' in mod
            ]
            # Create a list of services of the entire device
            self._services = self._services + self._nodes[i].services
            for mod in self._nodes[i].services:
                setattr(self, mod.alias, mod)

        self._cmd = defaultdict(lambda: defaultdict(lambda: None))
        self._cmd_data = []
        self._binary = []

        # We push our current state to make sure that
        # both our model and the hardware are synced.
        self._push_once()

    @property
    def services(self):
        return contList(self._services)

    @property
    def nodes(self):
        return nodeList(self._nodes)


    # Poll state from hardware.
    def _poll_once(self):
        self._state = self._io.read()
        if self._state != []:
            self._state['timestamp'] = time.time()
            return self._state
        return []

    def _poll_and_up(self):
        while self._running:
            if not self._pause:
                state = self._poll_once()
                if self._state != []:
                    self._update(state)
                    self._push_once()
            else:
                time.sleep(0.1)

    # Update our model with the new state.
    def _update(self, new_state):
        if 'dead_service' in new_state.keys():
            # We have lost a service put a flag on this service
            service_id = new_state['dead_service']
            # Find the service.
            for service in self._services:
                if (service.id == service_id):
                    s = "************************* EXCLUSION *************************\n"
                    s += "*  Service " + str(service.alias) + " have been excluded from the network due to no responses."
                    s += "\n*************************************************************"
                    print(s)
                    if (self._freedomLink != None):
                        self._freedomLink._kill(service.alias)
                    service._kill()
                    break

        if 'dead_node' in new_state.keys():
            # We have lost a node put a flag on all node services
            node_id = new_state['dead_node']
            for node in self._nodes:
                if (node.id == node_id):
                    s = "************************* EXCLUSION *************************\n"
                    s += "*  Node " + str(service.alias) + "have been excluded from the network due to no responses."
                    s += "\nThis exclude all services from this node :"
                    for service in node.services:
                        if (self._freedomLink != None):
                            self._freedomLink._kill(service.alias)
                        service._kill()
                        s += "\n*  Service " + str(service.alias) + " have been excluded from the network due to no responses."
                    
                    s += "\n*************************************************************"
                    print(s)
                    break

        if 'assert' in new_state.keys():
            # A node assert, print assert informations
            if (('node_id' in new_state['assert']) and ('file' in new_state['assert']) and ('line' in new_state['assert'])):
                s = "************************* ASSERT *************************\n"
                s += "*  Node " + str(new_state['assert']['node_id']) + " assert in file " + new_state['assert']['file'] + " line " + str(new_state['assert']['line'])
                s += "\n**********************************************************"
                print(s)
                # Consider this service as dead.
                # Find the service from it's node id.
                for node in self._nodes:
                    if (node.id == new_state['assert']['node_id']):
                        for service in node.services:
                            service._kill()
                        break
            if (self._freedomLink != None):
                self._freedomLink._assert(alias)
        if 'services' not in new_state.keys():
            return

        for alias, mod in new_state['services'].items():
            if hasattr(self, alias):
                getattr(self, alias)._update(mod)
            if (self._freedomLink != None):
                self._freedomLink._update(alias, mod)

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
                self._write(json.dumps({'services': self._cmd}).encode())
                self._cmd = defaultdict(lambda: defaultdict(lambda: None))
            for cmd, binary in zip(self._cmd_data, self._binary):
                time.sleep(0.01)
                self._write(json.dumps({'services': cmd}).encode() + '\n'.encode() + binary)

            self._cmd_data = []
            self._binary = []

    def _send(self, msg):
        with self._send_lock:
            self._io.send(msg)

    def _write(self, data):
        with self._send_lock:
            self._io.write(data)
