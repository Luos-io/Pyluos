import json
import logging
from mergedeep import merge, Strategy


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
            if data is None:
                return {}
            table = data.splitlines()
            if len(table) > 1:
                # load the Json of each substring
                jsn = [self.loads(sub_data) for sub_data in table]
                # merge all the Json data
                result = merge({}, *jsn, strategy=Strategy.ADDITIVE)
                return result
            else:
                return self.loads(data)
        except Exception as e:
            logging.getLogger(__name__).debug('Msg read failed: {}'.format(str(e)))
            if trials == 0:
                raise e

        return self.read(trials - 1)

    def recv(self):
        raise NotImplementedError

    def send(self, msg):
        self.write(self.dumps(msg))

    def write(self, data):
        self.write(data)

    def loads(self, data):
        if type(data) == bytes:
            data = data.decode()
            return json.loads(data)
        return []

    def dumps(self, msg):
        return json.dumps(msg).encode()


from .ws import Ws
from .serial_io import Serial

IOs = [Serial, Ws]


def io_from_host(host, *args, **kwargs):
    for cls in IOs:
        if cls.is_host_compatible(host):
            return cls(host=host, **kwargs)

    raise ValueError('No corresponding IO found (among {}).'.format(discover_hosts))


def discover_hosts():
    return sum([io.available_hosts() for io in IOs], [])
