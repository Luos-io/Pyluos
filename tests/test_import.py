import unittest


class TestImport(unittest.TestCase):
    def test_import_general(self):
        import pyluos

    def test_import_robot(self):
        from pyluos import Robot


if __name__ == '__main__':
    unittest.main()
