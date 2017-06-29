import unittest

from subprocess import Popen
from contextlib import closing

from pyrobus import Robot

host, port = '127.0.0.1', 9342


class TestWsRobot(unittest.TestCase):
    def setUp(self):
        self.fake_robot = Popen(['python', '../tools/fake_robot.py'])
        self.wait_for_server()

    def tearDown(self):
        self.fake_robot.terminate()
        self.fake_robot.wait()

    def test_init_command(self):
        with closing(Robot(host)) as robot:
            dxl = robot.my_dxl_1

            self.assertEqual(dxl.target_position, None)
            self.assertEqual(dxl.target_speed, None)
            self.assertEqual(dxl.compliant, None)
            self.assertEqual(dxl.wheel_mode, None)

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
