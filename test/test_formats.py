import unittest
import os
from slugify import slugify
import yaml


class TestFormat(unittest.TestCase):
    def setUp(self):
        self._data = {}
        for filename in os.listdir('./formats/mtg/'):
            if filename[-3:] == 'yml':
                with open('./formats/mtg/%s' % filename, 'r') as fileobj:
                    self._data[filename.split('.')[0]] = yaml.load(fileobj.read())


    def test_format_keys(self):
        for slug, item in self._data.items():
            for key in item.keys():
                assertTrue(key in ['inherits', 'sets', 'bans', 'assigns_commander_identity', 'has_sideboard',
                                   'is_singleton', 'maximum_deck_size', 'minium_deck_size', 'starting_life_total'])

    def test_inheritance(self):
        for slug, data in self._data.items():
            if data.get('inherits'):
                for item in data['inherits']:
                    self.assertTrue(slugify(item) in self._data)

        self.assertTrue(self._data)
