import json

from time import time
from random import randint
from threading import Timer

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.function(*self.args, **self.kwargs)
        self.start()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class FakeRobot(WebSocketHandler):
    period = 1 / 10
    verbose = False

    def open(self):
        if self.verbose:
            print('WebSocket connection open.')

        self.rt = RepeatedTimer(self.period, self.pub_state)

    def on_message(self, message):
        if self.verbose:
            print('{}: Received {}'.format(time(), message))

        self.handle_command(json.loads(message))

    def on_close(self):
        if self.verbose:
            print('WebSocket closed {}.'.format(self.close_reason))

        self.rt.stop()

    def pub_state(self):
        state = {
            'modules': [
                {
                    'alias': 'my_gate',
                    'id': 1,
                    'type': 'gate',
                },
                {
                    'alias': 'my_led',
                    'id': 2,
                    'type': 'led',
                },
                {
                    'alias': 'my_motor',
                    'id': 3,
                    'type': 'motor',
                },
                {
                    'alias': 'my_button',
                    'id': 4,
                    'type': 'button',
                    'value': 0,
                },
                {
                    'alias': 'my_potentiometer',
                    'id': 5,
                    'type': 'potard',
                    'value': 50,
                },
                {
                    'alias': 'my_relay',
                    'id': 6,
                    'type': 'relay',
                },
                {
                    'alias': 'my_distance',
                    'id': 7,
                    'type': 'distance',
                    'value': 12,
                },
                {
                    'alias': 'my_dxl_1',
                    'id': 8,
                    'type': 'dynamixel',
                    'position': randint(0, 180),
                },
                {
                    'alias': 'my_dxl_2',
                    'id': 9,
                    'type': 'dynamixel',
                    'position': randint(0, 180),
                    'speed': randint(0, 100),
                },
            ]
        }
        self.write_message(json.dumps(state))

    def handle_command(self, message):
        pass

    def check_origin(self, origin):
        return True


if __name__ == '__main__':
    port = 9342
    FakeRobot.verbose = True

    loop = IOLoop()
    app = Application([
        (r'/', FakeRobot)
    ])

    app.listen(port)
    url = 'ws://{}:{}'.format('127.0.0.1', port)
    print('Fake robot serving on {}'.format(url))
    loop.start()
