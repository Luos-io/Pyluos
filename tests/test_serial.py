import unittest


class TestSerialRobot(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_serial_host(self):
        from pyluos.io import Serial

        self.assertFalse(Serial.is_host_compatible('192.168.0.42'))


if __name__ == '__main__':
    unittest.main()
