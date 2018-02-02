import unittest

from contextlib import closing

from pyluos import Robot

import fakerobot


class TestWsRobot(fakerobot.TestCase):
    def test_init_command(self):
        with closing(Robot(fakerobot.host)) as robot:
            dxl = robot.my_dxl_1

            self.assertEqual(dxl.target_position, None)
            self.assertEqual(dxl.target_speed, None)
            self.assertEqual(dxl.compliant, None)
            self.assertEqual(dxl.wheel_mode, None)

    def test_switch_mode(self):
        with closing(Robot(fakerobot.host)) as robot:
            dxl = robot.my_dxl_1

            dxl.compliant = False
            self.assertEqual(dxl.compliant, False)

            dxl.wheel_mode = True
            dxl.wheel_mode = False

            self.assertEqual(dxl.compliant, True)


if __name__ == '__main__':
    unittest.main()
