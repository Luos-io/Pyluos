import unittest

from threading import Event
from subprocess import Popen
from contextlib import closing
from random import randint, choice
from string import ascii_lowercase

from pyrobus import Robot

host, port = '127.0.0.1', 9342


class TestWsRobot(unittest.TestCase):
    def setUp(self):
        self.fake_robot = Popen(['python', '../tools/fake_robot.py'])
        self.wait_for_server()

    def tearDown(self):
        self.fake_robot.terminate()
        self.fake_robot.wait()

    def test_life_cycle(self):
        robot = Robot(host)
        self.assertTrue(robot.alive)
        robot.close()
        self.assertFalse(robot.alive)

    def test_modules(self):
        with closing(Robot(host)) as robot:
            for mod in robot.modules:
                self.assertTrue(hasattr(robot, mod.alias))

    def test_cmd(self):
        with closing(Robot(host)) as robot:
            pos = randint(0, 180)
            robot.my_servo.position = pos
            self.assertEqual(robot.my_servo.position, pos)

    def test_possible_events(self):
        with closing(Robot(host)) as robot:
            for mod in robot.modules:
                self.assertTrue(isinstance(mod.possible_events, set))

            self.assertTrue('pressed' in robot.my_button.possible_events)

    def test_add_evt_cb(self):
        with closing(Robot(host)) as robot:
            robot.cb_trigger = Event()

            def dummy_cb(evt):
                robot.cb_trigger.set()

            evt = choice(list(robot.my_button.possible_events))
            robot.my_button.add_callback(evt, dummy_cb)
            robot.cb_trigger.wait()
            robot.my_button.remove_callback(evt, dummy_cb)

    def test_unknwon_evt(self):
        def dummy_cb(evt):
            pass

        with closing(Robot(host)) as robot:
            mod = robot.my_potentiometer
            while True:
                evt = ''.join(choice(ascii_lowercase)
                              for i in range(8))
                if evt not in mod.possible_events:
                    break

            with self.assertRaises(ValueError):
                mod.add_callback(evt, dummy_cb)

    def test_servoing_evt(self):
        with closing(Robot(host)) as robot:
            robot._synced = Event()

            def on_move(evt):
                robot.my_servo.position = evt.new_value
                robot._synced.set()

            robot.my_potentiometer.add_callback('moved',
                                                on_move)

            robot._synced.wait()
            self.assertEqual(robot.my_potentiometer.position,
                             robot.my_servo.position)

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
