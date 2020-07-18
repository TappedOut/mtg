import unittest
import os
import yaml


class TestFormat(unittest.TestCase):
    def setUp(self):
        self._data = {}
        for filename in os.listdir('./formats/mtg/'):
            if filename[-3:] == 'yml':
                with open('./formats/mtg/%s' % filename, 'r') as fileobj:
                    self._data[filename.split('.')[0]] = yaml.load(fileobj.read())


    def test_format_data(self):
        self.assertTrue(self._data)
