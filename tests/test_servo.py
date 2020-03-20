import unittest

from threading import Event
from contextlib import closing

from pyluos import Device

import fakerobot


# class TestWsRobot(fakerobot.TestCase):
#     def test_first_command(self):
#         with closing(Device(fakerobot.host)) as robot:
#             sent = Event()

#             def my_send(msg):
#                 sent.set()

#             robot._send = my_send

#             robot.my_servo.target_position = 0
#             sent.wait()

#     def test_speed_control(self):
#         with closing(Device(fakerobot.host)) as robot:
#             # Stop sync to make sure the fake robot
#             # does not change the position anymore.
#             robot.close()

#             servo = robot.my_servo

#             servo.target_speed = 0
#             self.assertEqual(servo.target_position, 90)

#             servo.target_position = 180
#             self.assertEqual(servo.target_speed, 100)


if __name__ == '__main__':
    unittest.main()
