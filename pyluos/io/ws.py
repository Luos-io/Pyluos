import socket
import websocket

from . import IOHandler


def resolve_hostname(hostname, port):
    # We do our own mDNS resolution
    # to enforce we only search for IPV4 address
    # and avoid a 5s timeout in the websocket on the ESP
    # See https://github.com/esp8266/Arduino/issues/2110

    addrinfo = socket.getaddrinfo(hostname, port,
                                  socket.AF_INET, 0,
                                  socket.SOL_TCP)
    addr = addrinfo[0][4][0]
    return addr


class Ws(IOHandler):
    @classmethod
    def is_host_compatible(cls, host):
        try:
            socket.inet_pton(socket.AF_INET, host)
            return True
        except socket.error:
            return host.endswith('.local')

    def __init__(self, host, port=9342):
        host = resolve_hostname(host, port)
        url = 'ws://{}:{}'.format(host, port)

        self._ws = websocket.create_connection(url)

    def is_ready(self):
        return True

    def recv(self):
        return self._ws.recv()

    def write(self, data):
        self._ws.send(data)

    def close(self):
        self._ws.close()
