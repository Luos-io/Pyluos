import unittest

from threading import Event
from contextlib import closing
from random import randint, choice
from string import ascii_lowercase

from pyluos import Device

import fakerobot


# class TestWsRobot(fakerobot.TestCase):
#     def test_life_cycle(self):
#         robot = Device(fakerobot.host)
#         self.assertTrue(robot.alive)
#         robot.close()
#         self.assertFalse(robot.alive)

#     def test_services(self):
#         with closing(Device(fakerobot.host)) as robot:
#             for mod in robot.services:
#                 self.assertTrue(hasattr(robot, mod.alias))

#     def test_cmd(self):
#         with closing(Device(fakerobot.host)) as robot:
#             pos = randint(0, 180)
#             robot.my_servo.position = pos
#             self.assertEqual(robot.my_servo.position, pos)

#     def test_possible_events(self):
#         with closing(Device(fakerobot.host)) as robot:
#             for mod in robot.services:
#                 self.assertTrue(isinstance(mod.possible_events, set))

#             self.assertTrue('pressed' in robot.my_button.possible_events)

#     def test_add_evt_cb(self):
#         with closing(Device(fakerobot.host)) as robot:
#             robot.cb_trigger = Event()

#             def dummy_cb(evt):
#                 robot.cb_trigger.set()

#             evt = choice(list(robot.my_button.possible_events))
#             robot.my_button.add_callback(evt, dummy_cb)
#             robot.cb_trigger.wait()
#             robot.my_button.remove_callback(evt, dummy_cb)

#     def test_unknwon_evt(self):
#         def dummy_cb(evt):
#             pass

#         with closing(Device(fakerobot.host)) as robot:
#             mod = robot.my_potentiometer
#             while True:
#                 evt = ''.join(choice(ascii_lowercase)
#                               for i in range(8))
#                 if evt not in mod.possible_events:
#                     break

#             with self.assertRaises(ValueError):
#                 mod.add_callback(evt, dummy_cb)

#     def test_servoing_evt(self):
#         with closing(Device(fakerobot.host)) as robot:
#             robot._synced = Event()

#             def on_move(evt):
#                 robot.my_servo.position = evt.new_value
#                 robot._synced.set()

#             robot.my_potentiometer.add_callback('moved',
#                                                 on_move)

#             robot._synced.wait()
#             self.assertEqual(robot.my_potentiometer.position,
#                              robot.my_servo.position)


if __name__ == '__main__':
    unittest.main()
