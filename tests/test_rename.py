import unittest
import random
import string

from contextlib import closing

from pyrobus import Robot

import fakerobot


class TestWsRobot(fakerobot.TestCase):
    def test_rename(self):
        with closing(Robot(fakerobot.host)) as robot:
            for _ in range(5):
                length = random.randint(1, robot._max_alias_length)
                mod = random.choice(robot.modules)

                old = mod.alias
                new = self.random_name(length)

                robot.rename_module(old, new)

                self.assertTrue(hasattr(robot, new))
                self.assertFalse(hasattr(robot, old))

    def test_unexisting_module(self):
        with closing(Robot(fakerobot.host)) as robot:
            while True:
                length = random.randint(1, robot._max_alias_length)
                name = self.random_name(length)

                if not hasattr(robot, name):
                    break

            with self.assertRaises(ValueError):
                robot.rename_module(name, 'oups')

    def test_loooooong_name(self):
        with closing(Robot(fakerobot.host)) as robot:
            mod = random.choice(robot.modules)

            length = random.randint(robot._max_alias_length + 1,
                                    robot._max_alias_length + 100)
            long_name = self.random_name(length)

            with self.assertRaises(ValueError):
                robot.rename_module(mod.alias, long_name)

    def random_name(self, length):
        return ''.join(random.choice(string.ascii_lowercase)
                       for _ in range(length))


if __name__ == '__main__':
    unittest.main()
