import json


class IOHandler(object):
    @classmethod
    def is_host_compatible(cls, host):
        return False

    def __init__(self, host):
        raise NotImplementedError

    def is_ready(self):
        raise NotImplementedError

    def read(self):
        try:
            data = self.recv()
            return self.loads(data)
        except Exception as e:
            import time
            msg = 'OUPS at {}: {}'.format(time.time(), str(e))
            print(msg)
            with open('/tmp/pyluos.log', 'a') as f:
                f.write(msg)
            return self.read()

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
