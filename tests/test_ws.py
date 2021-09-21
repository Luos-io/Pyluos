import unittest

from time import sleep
from contextlib import closing
from random import random

from pyluos import Device

import fakerobot


# class TestWsRobot(fakerobot.TestCase):
#     def test_ws_host(self):
#         from pyluos.io import Ws

#         self.assertTrue(Ws.is_host_compatible('127.0.0.1'))
#         self.assertTrue(Ws.is_host_compatible('192.168.0.42'))
#         self.assertTrue(Ws.is_host_compatible('Mundaka.local'))
#         self.assertTrue(Ws.is_host_compatible('10.0.0.12'))
#         self.assertFalse(Ws.is_host_compatible('/dev/ttyUSB0'))

#     def test_ws_connection(self):
#         with closing(Device(fakerobot.host)):
#             pass

#     def test_ws_reception(self):
#         with closing(Device(fakerobot.host)) as robot:
#             self.assertTrue(robot.services)
#             self.assertTrue(robot.name)

#     def test_spamming(self):
#         with closing(Device(fakerobot.host)) as robot:
#             robot.i = 0

#             def my_send(msg):
#                 robot._io.send(msg)
#                 robot.i += 1

#             robot._send = my_send

#             for p in range(180):
#                 robot.my_servo.position = p

#             sleep(robot._heartbeat_timeout + random())
#             self.assertTrue(robot.i < 10)
#             self.assertTrue(robot.alive)


if __name__ == '__main__':
    unittest.main()
