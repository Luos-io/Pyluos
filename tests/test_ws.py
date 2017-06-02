import unittest

from subprocess import Popen
from contextlib import closing

from robus import Robot


class TestWsRobot(unittest.TestCase):
    def setUp(self):
        self.fake_robot = Popen(['python', '../tools/fake_robot.py'])
        self.wait_for_server()

    def tearDown(self):
        self.fake_robot.terminate()
        self.fake_robot.wait()

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
            self.assertTrue(robot.name)

    def test_modules(self):
        with closing(Robot('127.0.0.1')) as robot:
            for mod in robot.modules:
                self.assertTrue(hasattr(robot, mod.alias))

    def wait_for_server(self):
        TIMEOUT = 30

        import socket
        import time

        from robus.io import Ws

        host, port = '127.0.0.1', Ws._port

        start = time.time()
        while (time.time() - start) < TIMEOUT:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                if sock.connect_ex((host, port)) == 0:
                    break
            time.sleep(0.1)
        else:
            raise EnvironmentError('Could not connect to fake robot!')


if __name__ == '__main__':
    unittest.main()
