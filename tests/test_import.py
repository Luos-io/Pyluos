import unittest


class TestImport(unittest.TestCase):
    def test_import_general(self):
        import pyluos

    def test_import_device(self):
        from pyluos import Device


if __name__ == '__main__':
    unittest.main()
