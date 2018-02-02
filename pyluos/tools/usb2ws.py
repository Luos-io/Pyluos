from threading import Thread

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

from pyluos.io.serial_io import Serial


class SerialToWs(WebSocketHandler):
    def open(self):
        print('Connection opened.')
        self.serial = Serial(self.serial_port)
        Thread(target=self._check_msg).start()

    def on_close(self):
        if self.verbose:
            print('Connection closed.')
        self.serial.close()

    def on_message(self, message):
        if self.verbose:
            print('WS->Ser: {}'.format(message))
        self.serial.write(message.encode())

    def send(self, message):
        if self.verbose:
            print('Ser->WS: {}'.format(message))
        self.ioloop.add_callback(lambda: self.write_message(message))

    def _check_msg(self):
        while True:
            self.send(self.serial.recv())

    def check_origin(self, origin):
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--serial-port', type=str, required=True)
    parser.add_argument('--ws-port', type=int, required=True)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    loop = IOLoop()

    SerialToWs.serial_port = args.serial_port
    SerialToWs.verbose = args.verbose
    SerialToWs.ioloop = loop

    app = Application([
        (r'/', SerialToWs)
    ])

    app.listen(args.ws_port)
    loop.start()


if __name__ == '__main__':
    main()
