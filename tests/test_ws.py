import unittest

from time import sleep
from subprocess import Popen
from contextlib import closing
from random import random

from pyrobus import Robot

host, port = '127.0.0.1', 9342


class TestWsRobot(unittest.TestCase):
    def setUp(self):
        self.fake_robot = Popen(['python', '../tools/fake_robot.py'])
        self.wait_for_server()

    def tearDown(self):
        self.fake_robot.terminate()
        self.fake_robot.wait()

    def test_ws_host(self):
        from pyrobus.io import Ws

        self.assertTrue(Ws.is_host_compatible('127.0.0.1'))
        self.assertTrue(Ws.is_host_compatible('192.168.0.42'))
        self.assertTrue(Ws.is_host_compatible('Mundaka.local'))
        self.assertTrue(Ws.is_host_compatible('10.0.0.12'))
        self.assertFalse(Ws.is_host_compatible('/dev/ttyUSB0'))

    def test_ws_connection(self):
        with closing(Robot(host)):
            pass

    def test_life_cycle(self):
        robot = Robot(host)
        self.assertTrue(robot.alive)
        robot.close()
        self.assertFalse(robot.alive)

    def test_ws_reception(self):
        with closing(Robot(host)) as robot:
            self.assertTrue(robot.modules)
            self.assertTrue(robot.name)

    def test_modules(self):
        with closing(Robot(host)) as robot:
            for mod in robot.modules:
                self.assertTrue(hasattr(robot, mod.alias))

    def test_spamming(self):
        with closing(Robot(host)) as robot:
            robot.i = 0

            def my_send(msg):
                robot._io.send(msg)
                robot.i += 1

            robot._send = my_send

            for p in range(180):
                robot.my_servo.position = p

            sleep(robot._heartbeat_timeout + random())
            self.assertTrue(robot.i < 10)
            self.assertTrue(robot.alive)

    def wait_for_server(self):
        TIMEOUT = 30

        import socket
        import time

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
