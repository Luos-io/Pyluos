from __future__ import division

import time
import socket

from contextlib import closing
from threading import Thread, Event

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from pyluos.tools import usb_gate, wifi_gate


class Publisher(WebSocketHandler):
    verbose = False

    gates = []
    pub = Event()

    def open(self):
        if self.verbose:
            print('WebSocket connection open.')

        self.publish_gates()
        self.pub_in_bg()

    def on_close(self):
        if self.verbose:
            print('WebSocket closed {}.'.format(self.close_reason))

    def publish_gates(self):
        self.ioloop.add_callback(self._real_pub)

    def _real_pub(self):
        if self.verbose:
            print('Send: {}'.format(Publisher.gates))

        self.write_message(Publisher.gates)

    def pub_in_bg(self):
        def _pub():
            while True:
                self.pub.wait()
                self.publish_gates()
                self.pub.clear()

        t = Thread(target=_pub)
        t.daemon = True
        t.start()

    def check_origin(self, origin):
        return True


def connect(host, port):
    loop = IOLoop()

    Publisher.verbose = False
    Publisher.ioloop = loop

    app = Application([
        (r'/', Publisher)
    ])

    app.listen(port)
    url = 'ws://{}:{}'.format(host, port)
    if Publisher.verbose:
        print('Fake robot serving on {}'.format(url))
    t = Thread(target=loop.start)
    t.daemon = True
    t.start()


def update(gates):
    Publisher.gates = gates
    Publisher.pub.set()


def free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port


def main():
    usb_gates = {}
    redirect = {}
    usb2ws = {}

    wifi_gates = {}

    connect('127.0.0.1', 9090)

    while True:
        # Deal with USB gates
        found_usb_gates = usb_gate.discover()

        unplugged_gates = set(usb_gates) - set(found_usb_gates)
        for g in unplugged_gates:
            print('Gate "{}" unplugged.'.format(usb_gates[g]))

            print('--> Stop its redirection.')
            redirect.pop(g)
            usb2ws.pop(g).terminate()

        plugged_gates = set(found_usb_gates) - set(usb_gates)
        for g in plugged_gates:
            print('Gate "{}" plugged.'.format(found_usb_gates[g]))

            ws_port = free_port()
            print('--> Redirecting it to "ws://127.0.0.1:{}".'.format(ws_port))
            p = usb_gate.redirect_to_ws(found_usb_gates[g], ws_port)
            redirect[g] = ws_port
            usb2ws[g] = p

        usb_gates = found_usb_gates

        # Deal with WiFi gate
        found_wifi_gates = wifi_gate.discover()

        lost_gates = set(wifi_gates) - set(found_wifi_gates)
        for g in lost_gates:
            print('Gate "{}" lost.'.format(g))

        discovered_gates = set(found_wifi_gates) - set(wifi_gates)
        for g in discovered_gates:
            print('Gate "{}" discovered.'.format(g))

        wifi_gates = found_wifi_gates

        gates = {}
        for name in usb_gates.keys():
            gates[name] = {'host': '127.0.0.1', 'port': redirect[name]}

        for name, (host, port) in wifi_gates.items():
            gates[name] = {'host': host, 'port': port}

        update(gates)

        time.sleep(1.)


if __name__ == '__main__':
    main()
