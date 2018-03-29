from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

from pyluos import Robot
from pyluos.io import IOHandler
from pyluos.tools import scratch


class UsbHandler(IOHandler):
    def __init__(self, host):
        self.robot = Robot(host)
        self.io = self.robot._io

        self.ws = None

    def write(self, msg):
        self.io.write(msg)

    def is_ready(self):
        return self.io.is_ready()

    def recv(self):
        message = self.io.recv()
        if self.ws is not None:
            self.ws.ioloop.add_callback(lambda: self.ws.write_message(message))
        return message


class WsHandler(WebSocketHandler):
    def open(self):
        if self.robot._io.ws is not None:
            self.robot._io.ws.close()

        self.robot._io.ws = self

    def on_close(self):
        self.robot._io.ws = None

    def on_message(self, message):
        self.robot._io.write(message.encode())

    def check_origin(self, origin):
        return True


class HttpScratchHandler(RequestHandler):
    def get(self):
        self.write(self.extension)


class Test(RequestHandler):
    def get(self):
        self.write("hello")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('serial_port', type=str)
    parser.add_argument('--port', type=int, default=9342)
    parser.add_argument('--hostname', type=str, default='localhost')
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    robot = Robot(args.serial_port, IO=UsbHandler)

    loop = IOLoop()
    app = Application([
        (r'/', WsHandler),
        (r'/scratch-extension', HttpScratchHandler),
    ])

    WsHandler.robot = robot
    WsHandler.ioloop = loop
    WsHandler.verbose = args.verbose

    ext = scratch.generate_extension('luos', robot, args.hostname, args.port)
    HttpScratchHandler.extension = ext

    print('Scratch extension url: "http://{}:{}/scratch-extension"'.format(args.hostname, args.port))

    app.listen(args.port)
    loop.start()


if __name__ == '__main__':
    main()
