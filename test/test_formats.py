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
                self.assertTrue(key in ['inherits', 'sets', 'bans', 'assigns_commander_identity', 'has_sideboard',
                                        'is_singleton', 'maximum_deck_size', 'minium_deck_size', 'starting_life_total'])

    def test_inheritance(self):
        for slug, data in self._data.items():
            if data.get('inherits'):
                for item in data['inherits']:
                    self.assertTrue(slugify(item) in self._data)

        self.assertTrue(self._data)

    def test_recursion(self):
        def recurse(slug, inherit_key, inherit_target, illegal_items=[]):
            illegal_items.append(slug)
            inherits = map(slugify, self._data[slug][inherit_key])
            for inspect_slug, data in self._data.items():
                if inspect_slug not in inherits:
                    continue
                for item in data.get(inherit_target) or []:
                    yield item
                if data.get(inherit_key):
                    self.assertFalse(data[inherit_key] in illegal_items)
                    recurse(inspect_slug, inherit_key, inherit_target, illegal_items=illegal_items)

        for slug, data in self._data.items():
            bans = data.get('bans') or []
            sets = data.get('sets') or []
            previous_bans = len(bans)
            previous_sets = len(sets)

            if data.get('inherits'):
                print("inherits: %s" % data['inherits'])
                sets += list(recurse(slug, 'inherits', 'sets'))
                self.assertTrue(previous_sets < len(sets), "%s didn't end up with additional sets despite inheriting %s" % (slug, data['inherits']))
