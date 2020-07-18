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
        for slug, item in self._data.items():
            for key in item.keys():
                self.assertTrue(key in ['inherits', 'sets', 'bans', 'assigns_commander_identity', 'has_sideboard',
                                        'is_singleton', 'maximum_deck_size', 'minium_deck_size', 'starting_life_total'], "%s has a bad key %s" % (slug, key))

    def test_inheritance(self):
        for slug, data in self._data.items():
            for item in data.get('inherits') or []:
                self.assertTrue(slugify(item) in self._data)
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
                    self.assertTrue(slugify(item) not in redundant_objects, "Redundant %s found within %s: %s" % (inherit_target, slug, item))
                    redundant_objects.append(slugify(item))
                    yield item
                if data.get(inherit_key):
                    self.assertFalse(data[inherit_key] in redundant_slugs)
                    recurse(inspect_slug, inherit_key, inherit_target, redundant_slugs=redundant_slugs, redundant_objects=redundant_objects)
            log.info(locals())
            self.assertFalse(redundant_objects == [], "No items collected during inheritance")

        for slug, data in self._data.items():
            bans = data.get('bans') or []
            sets = data.get('sets') or []
            previous_bans = len(bans)
            previous_sets = len(sets)

            if data.get('inherits'):
                log.info("inherits: %s" % data['inherits'])
                sets += list(recurse(slug, 'inherits', 'sets'))
                self.assertTrue(previous_sets < len(sets), "%s still only had %s sets despite inheriting %s" % (slug, previous_sets, data['inherits']))
