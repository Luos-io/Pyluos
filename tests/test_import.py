import unittest


class TestImport(unittest.TestCase):
    def test_import_general(self):
        import robus

    def test_import_robot(self):
        from robus import Robot


if __name__ == '__main__':
    unittest.main()
