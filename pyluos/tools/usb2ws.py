from threading import Thread

from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer

from pyluos.io.serial_io import Serial


class SerialToWs(WebSocket):
    def handleConnected(self):
        print('Connection opened.')
        self.serial = Serial(self.serial_port)

        self.t = Thread(target=self._check_msg)
        self.t.daemon = True
        self.t.start()

    def handleClose(self):
        if self.verbose:
            print('Connection closed.')
        self.serial.close()

    def handleMessage(self):
        message = self.data

        if self.verbose:
            print('WS->Ser: {}'.format(message))

        try:
            message = message.encode()
            self.serial.write(message)

        except UnicodeDecodeError:
            print("Fail")
            pass


    def send(self, message):
        if self.verbose:
            print('Ser->WS: {}'.format(message))
        self.sendMessage(message)

    def _check_msg(self):
        while True:
            r = self.serial.recv()
            try:
                self.send(r)
            except UnicodeDecodeError:
                print('Fail', r)

        print('LOOP OVER!')


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--serial-port', type=str, required=True)
    parser.add_argument('--ws-port', type=int, required=True)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    SerialToWs.serial_port = args.serial_port
    SerialToWs.verbose = args.verbose

    io_server = SimpleWebSocketServer('', args.ws_port, SerialToWs)
    io_server.serveforever()


if __name__ == '__main__':
    main()
