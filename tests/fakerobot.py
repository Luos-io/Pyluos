import unittest
import socket
import time

from subprocess import Popen
from contextlib import closing


TIMEOUT = 30
host, port = '127.0.0.1', 9342


class TestCase(unittest.TestCase):
    def setUp(self):
        self._fake_robot = Popen(['python', '../tools/fake_robot.py'])
        wait_for_server()

    def tearDown(self):
        self._fake_robot.terminate()
        self._fake_robot.wait()


def wait_for_server():
    start = time.time()
    while (time.time() - start) < TIMEOUT:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                break
        time.sleep(0.1)
    else:
        raise EnvironmentError('Could not connect to fake robot!')
