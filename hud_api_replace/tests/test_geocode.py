from django.test import TestCase
from mock import MagicMock, patch
from django.db import IntegrityError

import time

from hud_api_replace.geocode import geocode_get_data, _extract_zip_code
from hud_api_replace.models import CachedGeodata


class TestGeocode(TestCase):
    def test_extract_zip_code__empty(self):
        """Testing _extract_zip_code, with empty argument."""
        result = _extract_zip_code('')
        self.assertEqual(result, '')

    def test_extract_zip_code__zipcode(self):
        """Testing _extract_zip_code, with zip code."""
        result = _extract_zip_code('20005')
        self.assertEqual(result, '20005')
        result = _extract_zip_code('20005-1999')
        self.assertEqual(result, '20005-1999')

    def test_extract_zip_code__address(self):
        """Testing _extract_zip_code, with a key generated from an address."""
        result = _extract_zip_code('123 NONE SOME ST.|WASHINGTON,DC|20005')
        self.assertEqual(result, '20005')

    def test_geocode_get_data__existent(self):
        """Testing geocode_get_data, with cached argument."""
        cg = CachedGeodata(key='20005', lat=111, lon=222, expires=time.time() + 10000)
        cg.save()
        result = geocode_get_data('20005')
        self.assertTrue('zip' in result)
        self.assertEqual(result['zip']['zipcode'], '20005')
        self.assertEqual(result['zip']['lat'], 111)
        self.assertEqual(result['zip']['lng'], 222)
