import unittest
import os
import logging
from slugify import slugify
import yaml


log = logging.getLogger(__name__)


class TestFormat(unittest.TestCase):
    def setUp(self):
        self._data = {}
        for filename in os.listdir('./formats/mtg/'):
            if filename[-3:] == 'yml':
                with open('./formats/mtg/%s' % filename, 'r') as fileobj:
                    self._data[filename.split('.')[0]] = yaml.load(fileobj.read())


    def test_format_keys(self):
        object_types = {
            'inherits': list,
            'sets': list,
            'bans': list,
            'banned_as_commander': list,
            'has_commander': bool,
            'has_sideboard': bool,
            'is_singleton': bool,
            'maximum_deck_size': int,
            'minimum_deck_size': int,
            'starting_life_total': int,
        }

        for slug, item in self._data.items():
            for key in item.keys():
                self.assertTrue(key in object_types, "%s has a bad key %s" % (slug, key))
                self.assertTrue(isinstance(item[key], object_types[key]), "%s had bad data type for key %s (should be %s)" % (slug, key, object_types[key]))

    def test_inheritance(self):
        for slug, data in self._data.items():
            self.assertTrue(data, "%s.yml contained no data" % slug)
            for item in data.get('inherits') or []:
                self.assertTrue(slugify(item) in self._data, "%s found inheriting a bad format %s" % (slug, item))
        self.assertTrue(self._data)

    def test_recursion(self):
        def recurse(slug, inherit_key, inherit_target, redundant_slugs=None, redundant_objects=None):
            redundant_slugs = redundant_slugs or []
            redundant_objects = redundant_objects or []
            redundant_slugs.append(slug)
            inherits = list(map(slugify, self._data[slug][inherit_key]))
            for inspect_slug, data in self._data.items():
                if inspect_slug not in inherits:
                    continue
                for item in data.get(inherit_target) or []:
                    # self.assertTrue(slugify(item) not in redundant_objects, "Redundant %s found within %s: %s %s" % (inherit_target, slug, item, locals()))
                    redundant_objects.append(slugify(item))
                    yield item
                if data.get(inherit_key):
                    self.assertFalse(data[inherit_key] in redundant_slugs)
                    for item in recurse(inspect_slug, inherit_key, inherit_target, redundant_slugs=redundant_slugs, redundant_objects=redundant_objects):
                        yield item

        for slug, data in self._data.items():
            bans = data.get('bans') or []
            sets = data.get('sets') or []
            previous_bans = len(bans)
            previous_sets = len(sets)

            if data.get('inherits'):
                log.info("inherits: %s" % data['inherits'])
                sets += list(recurse(slug, 'inherits', 'sets'))
                self.assertTrue(previous_sets < len(sets), "%s still only had %s sets despite inheriting %s" % (slug, previous_sets, data['inherits']))
