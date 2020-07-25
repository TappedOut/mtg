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
        for filename in os.listdir('./formats/'):
            if filename[-3:] == 'yml':
                with open('./formats/%s' % filename, 'r') as fileobj:
                    self._format_data[filename.split('.')[0]] = yaml.load(fileobj.read())

    def test_sets(self):
        for slug, item in self._set_data.items():
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
            'draft_logic': str,
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

    def test_cards(self):
        for filename in os.listdir('./cards/'):
            if filename[-3:] == 'yml':
                with open('./cards/%s' % filename, 'r') as fileobj:
                    self._cardtest_inner(yaml.load(fileobj.read()))

    def _printingtest_inner(self, data):
        def in_sets(val):
            return slugify(val) in self._set_data

        validates = {
            'name': in_sets,
        }
        object_types = {
            'name': str,
            'tla': str,
            'url': str,
            'variations': list,
            'set_number': int,
        }

    def _cardtest_inner(self, data):
        def in_formats(vals):
            for val in vals:
                self.assertTrue(slugify(val) in self._format_data, "Bad format value: %s" % val)
            return True

        validates = {
            'formats': in_formats,
        }
        object_types = {
            'companions': list,
            'has_activated_abilities': bool,
            'activated_abilities': list,
            'is_permanent': bool,
            'cannonical_set': str,
            'all_printings': list,
            'booster_exclude': bool,
            'canadian_hl_score': int,
            'cannonical_type': str,
            'effective_cost': list,
            'flat_cost': int,
            'foil': bool,
            'formats': list,
            'url': str,
            'image_large': str,
            'is_basic_land': bool,
            'is_limitless': bool,
            'keywords': list,
            'mana_cost': str,
            'mana_cost_converted': int,
            'mana_produced': str,
            'name': str,
            'power_toughness': str,
            'slug': str,
            'tap_land': bool,
            'is_back': bool,
            'is_front': bool,
            'is_land': bool,
            'type': str,
            'subtype': str,
            'wizards_id': str,
            'wizards_url': str,
            'rules': str,
            'tokens': list,
            'subtype_tokens': list,
            'mtgo_foil_id': int,
            'mtgo_id': int,
            'activation_costs': list,
            'promo_sets': list,
            'flip': str,
        }
        for key in data.keys():
            self.assertTrue(key in object_types, "Bad key %s found for %s" % (key, data['slug']))
            self.assertTrue(isinstance(data[key], object_types[key]), "%s had bad data type for key %s (should be %s but found %s)" % (data['slug'], key, object_types[key], data[key].__class__))
            self.assertTrue(key in object_types, "Bad key %s found in %s" % (key, data['slug']))
            if key in data and data.get(key) is not None:
                self.assertTrue(isinstance(data[key], object_types[key]), "%s had bad data type for key %s (should be %s but found %s)" % (data['slug'], key, object_types[key], data[key].__class__))
            if key in validates:
                self.assertTrue(validates[key](data.get(key)), "Bad value for %s.%s found" % (data['slug'], key))
        self._printingtest_inner(data['all_printings'])
