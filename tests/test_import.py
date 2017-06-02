import unittest


class TestImport(unittest.TestCase):
    def test_import_general(self):
        import pyrobus

    def test_import_robot(self):
        from pyrobus import Robot


if __name__ == '__main__':
    unittest.main()
