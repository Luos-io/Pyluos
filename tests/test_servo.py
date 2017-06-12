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

    def test_speed_control(self):
        with closing(Robot(host)) as robot:
            # Stop sync to make sure the fake robot
            # does not change the position anymore.
            robot.close()

            servo = robot.my_servo

            servo.speed = 0
            self.assertEqual(servo.position, 90)

            servo.position = 180
            self.assertEqual(servo.speed, 100)

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
