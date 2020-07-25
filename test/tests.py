import unittest
import os
import datetime
import logging
from slugify import slugify
import yaml


log = logging.getLogger(__name__)


class TestData(unittest.TestCase):
    def setUp(self):
        self._set_data = {}
        with open('./sets.yml', 'r') as fileobj:
            for item in yaml.load(fileobj):
                self._set_data[slugify(item['name'])] = item

        self._format_data = {}
        for filename in os.listdir('./formats/mtg/'):
            if filename[-3:] == 'yml':
                with open('./formats/mtg/%s' % filename, 'r') as fileobj:
                    self._format_data[filename.split('.')[0]] = yaml.load(fileobj.read())

    def test_sets(self):
        for slug, item in self._format_data.items():
            for setitem in item.get('sets') or []:
                self.assertTrue(slugify(setitem) in self._set_data, "%s under %s was not found in the set data" % (setitem, slug))

    def test_set_keys(self):
        object_types = {
            'name': str,
            'card_count': int,
            'tla': str,
            'wizards_tla': str,
            'third_tla': str,
            'block': str,
            'tcgplayer_skip': bool,
            'chaos_skip': bool,
            'ck_skip': bool,
            'core': bool,
            'tcgplayer_alt': str,
            'chaos_alt': str,
            'ck_alt': str,
            'foil_only': bool,
            'can_draft': bool,
            'is_mtgo': bool,
            'border_color': str,
            'cannonical_image': bool,
            'cannonical_price': bool,
            'applies_legality': bool,
            'release_date': datetime.date,
            'standard_expiry': datetime.date,

        }
        def border_color(val):
            if val:
                return val in ['W', 'G', 'B']
            return True  # blank = B
        validates = {
            'border_color': border_color,
        }

        for slug, item in self._set_data.items():
            for key in item.keys():
                self.assertTrue(isinstance(item[key], object_types[key]), "%s had bad data type for key %s (should be %s but found %s)" % (slug, key, object_types[key], item[key].__class__))
                self.assertTrue(key in object_types, "Bad key %s found in %s" % (key, slug))
                if key in item:
                    self.assertTrue(isinstance(item[key], object_types[key]), "%s had bad data type for key %s (should be %s but found %s)" % (slug, key, object_types[key], item[key].__class__))
                if key in validates:
                    self.assertTrue(validates[key](item.get(key)), "Bad value for %s.%s found: %s" % (slug, key, item.get(key)))

    def test_format_keys(self):
        object_types = {
            'inherits': list,
            'sets': list,
            'bans': list,
            'banned_as_commander': list,
            'has_commander': bool,
            'has_sideboard': bool,
            'is_singleton': bool,
            'sideboard_size': int,
            'maximum_deck_size': int,
            'minimum_deck_size': int,
            'starting_life_total': int,
        }

        for slug, item in self._format_data.items():
            for key in item.keys():
                self.assertTrue(key in object_types, "%s has a bad key %s" % (slug, key))
                self.assertTrue(isinstance(item[key], object_types[key]), "%s had bad data type for key %s (should be %s)" % (slug, key, object_types[key]))

    def test_format_inheritance(self):
        for slug, data in self._format_data.items():
            self.assertTrue(data, "%s.yml contained no data" % slug)
            for item in data.get('inherits') or []:
                self.assertTrue(slugify(item) in self._format_data, "%s found inheriting a bad format %s" % (slug, item))
        self.assertTrue(self._format_data)

    def test_format_recursion(self):
        def recurse(slug, inherit_key, inherit_target, redundant_slugs=None, redundant_objects=None):
            redundant_slugs = redundant_slugs or []
            redundant_objects = redundant_objects or []
            redundant_slugs.append(slug)
            inherits = list(map(slugify, self._format_data[slug][inherit_key]))
            for inspect_slug, data in self._format_data.items():
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

        for slug, data in self._format_data.items():
            bans = data.get('bans') or []
            sets = data.get('sets') or []
            previous_bans = len(bans)
            previous_sets = len(sets)

            if data.get('inherits'):
                log.info("inherits: %s" % data['inherits'])
                sets += list(recurse(slug, 'inherits', 'sets'))
                self.assertTrue(previous_sets < len(sets), "%s still only had %s sets despite inheriting %s" % (slug, previous_sets, data['inherits']))
