import json
import logging


class IOHandler(object):
    @classmethod
    def is_host_compatible(cls, host):
        return False

    def __init__(self, host):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def read(self, trials=5):
        try:
            data = self.recv()
            return self.loads(data)
        except Exception as e:
            logging.getLogger(__name__).debug('Msg read failed: {}'.format(str(e)))
            if trials == 0:
                raise e

        return self.read(trials)

    def recv(self):
        raise NotImplementedError

    def send(self, msg):
        self.write(self.dumps(msg))

    def write(self, data):
        raise NotImplementedError

    def loads(self, data):
        if type(data) == bytes:
            data = data.decode()
        return json.loads(data)

    def dumps(self, msg):
        return json.dumps(msg).encode()


from .ws import Ws
from .serial_io import Serial

IOs = [Serial, Ws]


def io_from_host(host, *args, **kwargs):
    for cls in IOs:
        if cls.is_host_compatible(host):
            return cls(host=host, *args, **kwargs)

    raise ValueError('No corresponding IO found (among {}).'.format(discover_hosts))


def discover_hosts():
    return sum([io.available_hosts() for io in IOs], [])
