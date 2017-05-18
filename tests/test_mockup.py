import unittest

from subprocess import Popen
from contextlib import closing

from robus import Robot


class TestMockup(unittest.TestCase):
    _multiprocess_shared_ = True

    @classmethod
    def setup_class(cls):
        cls.fake_robot = Popen(['python', '../tools/fake_robot.py'])
        cls.wait_for_server()

    def test_ws_host(self):
        from robus.io import Ws

        self.assertTrue(Ws.is_host_compatible('127.0.0.1'))
        self.assertTrue(Ws.is_host_compatible('192.168.0.42'))
        self.assertTrue(Ws.is_host_compatible('Mundaka.local'))
        self.assertTrue(Ws.is_host_compatible('10.0.0.12'))
        self.assertFalse(Ws.is_host_compatible('/dev/ttyUSB0'))

    def test_ws_connection(self):
        with closing(Robot('127.0.0.1')):
            pass

    def test_ws_reception(self):
        with closing(Robot('127.0.0.1')) as robot:
            self.assertTrue(robot.modules)

    def test_modules(self):
        with closing(Robot('127.0.0.1')) as robot:
            for mod in robot.modules:
                self.assertTrue(hasattr(robot, mod.alias))

    @classmethod
    def teardown_class(cls):
        cls.fake_robot.terminate()
        cls.fake_robot.wait()

    @classmethod
    def wait_for_server(cls):
        import socket
        import time

        from robus.io import Ws

        host, port = '127.0.0.1', Ws._port

        while True:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex((host, port)) == 0:
                    break
            time.sleep(0.1)


if __name__ == '__main__':
    unittest.main()
