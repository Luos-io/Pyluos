import threading
import websocket
import json

from .modules import (name2mod, msg_stack)


class Robot(object):
    _ws_port = 9342

    def __init__(self, host):
        url = 'ws://{}:{}'.format(host, self._ws_port)
        self._ws = websocket.create_connection(url)

        # We force a first poll to setup our model.
        self._setup(self._poll_once())

        # Setup both poll/push synchronization loops.
        self._poll_bg = threading.Thread(target=self._poll_and_up)
        self._poll_bg.daemon = True
        self._poll_bg.start()
        self._push_bg = threading.Thread(target=self._push_update)
        self._push_bg.daemon = True
        self._push_bg.start()

    def _setup(self, state):
        self.modules = [
            name2mod[mod['type']](mod['id'], mod['alias'])

            for mod in state['modules']
        ]
        # We push our current state to make sure that
        # both our model and the hardware are synced.
        self._push_once()

        for mod in self.modules:
            setattr(self, mod.alias, mod)

    # Poll state from hardware.
    def _poll_once(self):
        return json.loads(self._ws.recv())

    def _poll_and_up(self):
        while True:
            new_state = self._poll_once()
            self._update(new_state)

    # Update our model with the new state.
    def _update(self, new_state):
        for mod in new_state['modules']:
            if 'value' in mod and hasattr(self, mod['alias']):
                getattr(self, mod['alias'])._update(mod)

    # Push update from our model to the hardware
    def _push_once(self):
        data = {}
        while not msg_stack.empty():
            msg = msg_stack.get()
            data.update(msg)

        if data:
            self._send({
                'modules': data
            })

    def _push_update(self):
        while True:
            msg = msg_stack.get()
            self._send({
                'modules': msg
            })

    def _send(self, msg):
        self._ws.send(json.dumps(msg))
