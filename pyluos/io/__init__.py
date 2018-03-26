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

            if trials > 0:
                return self.read(trials - 1)
            else:
                raise e

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


def io_from_host(host, *args, **kwargs):
    for cls in [Ws, Serial]:
        if cls.is_host_compatible(host):
            return cls(host=host, *args, **kwargs)
    raise ValueError('No corresponding IO found.')
