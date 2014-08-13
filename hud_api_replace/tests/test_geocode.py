from django.test import TestCase
from mock import MagicMock, patch
from django.db import IntegrityError

import time

from hud_api_replace.geocode import (
    GoogleGeocode, _geocode_compute_key, _extract_zip_code, _geocode_cached_data, _convert_data, geocode_get_data)
from hud_api_replace.models import CachedGeodata


class TestGoogleGeocode(TestCase):
    def setUp(self):
        self.gc = GoogleGeocode(20005)

    def test_init(self):
        """ Testing __init__ """
        self.assertEqual(self.gc.zipcode, 20005)
        self.assertEqual(type(self.gc.invisible_zipcodes), dict)
        self.assertTrue(len(self.gc.invisible_zipcodes) > 0)
        self.assertTrue(self.gc.privateKey is not None)
        self.assertTrue(self.gc.clientID is not None)

    def test_is_usa_or_territory__correct(self):
        """ Testing is_usa_or_territory, GUAM, USVI, ASamoa, PRico, Cnmi, Rmi, Usa """
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, GUAM something else"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, UsVi"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, American Samoa else"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, Puerto Rico something else"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, Cnmi"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, rmi"))
        self.assertTrue(self.gc.is_usa_or_territory("123 Address, Usa"))

    def test_is_usa_or_territory__wrong(self):
        """ Testing is_usa_or_territory, Not USA address """
        self.assertFalse(self.gc.is_usa_or_territory("123 Address, Mexico City, Mexico"))

    def test_signed_url__correct(self):
        """ Testing signed_url, correct url """
        url = "http://maps.googleapis.com/maps/api/geocode/json?address=New+York&sensor=false&client=clientID"
        expected = "http://maps.googleapis.com/maps/api/geocode/json?address=New+York&sensor=false&client=clientID&signature=KrU1TzVQM7Ur0i8i7K3huiw3MsA="
        self.gc.privateKey = "vNIXE0xscrmjlyV-12Nj_BvUPaw="
        self.gc.clientID = "clientID"
        signed_url = self.gc.signed_url(url)
        self.assertEqual(signed_url, expected)

    def test_signed_url__empty(self):
        """ Testing signed_url, empty url """
        url = ''
        signed_url = self.gc.signed_url(url)
        self.assertEqual(signed_url, None)

    @patch('urllib2.urlopen')
    def test_request_google_maps(self, mock_urlopen):
        """ Testing request_google_maps """
        def urlopen_check_param(param):
            self.param = param
            mm = MagicMock()
            mm.read.return_value = '{"Success":"success"}'
            return mm

        mock_urlopen.side_effect = urlopen_check_param
        expected = "http://maps.googleapis.com/maps/api/geocode/json?address=20005&sensor=false&client=" + self.gc.clientID
        response = self.gc.request_google_maps(20005)
        self.assertTrue(expected in self.param)
        self.assertEqual(response['Success'], 'success')

    def test_geocode_compute_key__empty(self):
        """Testing _geocode_compute_key, with empty argument."""
        result = _geocode_compute_key('')
        self.assertEqual(result, '')

    def test_geocode_compute_key__zipcode(self):
        """Testing _geocode_compute_key, zipcode as argument."""
        result = _geocode_compute_key('20005')
        self.assertEqual(result, '20005')
        result = _geocode_compute_key('20005-1999')
        self.assertEqual(result, '20005-1999')

    def test_geocode_compute_key__address(self):
        """Testing _geocode_compute_key, with an address."""
        result = _geocode_compute_key('123 Some str, Washington DC, 20005')
        self.assertEqual(result, '123 NONE SOME ST.|WASHINGTON,DC|20005')

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

    def test_geocode_cached_data__new(self):
        """Testing _geocode_cached_data, with an arg that is not in caches."""
        self.assertRaises(Exception, _geocode_cached_data, 'DEFINITELY-NOT-CACHED')

    def test_geocode_cached_data__existent(self):
        """Testing _geocode_cached_data, with empty argument."""
        cg = CachedGeodata(key='NEW-RECORD', lat=1, lon=2, expires=time.time() + 10000)
        cg.save()
        result = _geocode_cached_data('NEW-RECORD')
        self.assertTrue('result' in result)
        self.assertEqual(result['result'][0], 'NEW-RECORD')
        self.assertEqual(result['result'][1], 1)
        self.assertEqual(result['result'][2], 2)

    def test_geocode_cached_data__expired(self):
        """Testing _geocode_cached_data, with an expired record."""
        cg = CachedGeodata(key='EXPIRED-RECORD', lat=1, lon=2, expires=time.time() - 10)
        cg.save()
        self.assertRaises(Exception, _geocode_cached_data, 'EXPIRED-RECORD')

    def test_convert_data__good_data(self):
        """Testing _convert_data, with an expected data structure."""
        data = {'result': ['20005', 'LAT', 'LON']}
        result = _convert_data(data)
        self.assertTrue('zip' in result)
        self.assertEqual(result['zip']['zipcode'], '20005')
        self.assertEqual(result['zip']['lat'], 'LAT')
        self.assertEqual(result['zip']['lng'], 'LON')

    def test_conver_data__bad_data(self):
        """Testing _convert_data, with bad data structure."""
        data = {'esult': ['20005', 'LAT', 'LON']}
        result = _convert_data(data)
        self.assertEqual(result, data)

    @patch('hud_api_replace.geocode.GoogleGeocode.google_maps_api')
    def test_geocode_get_data__new(self, mock_geocode):
        """Testing geocode_get_data, with new argument."""
        mock_geocode.return_value = {'result': ['20005', 11, 22]}
        result = geocode_get_data('DEFINITELY-NOT_CACHED')
        self.assertTrue('zip' in result)
        self.assertEqual(result['zip']['zipcode'], '20005')
        self.assertEqual(result['zip']['lat'], 11)
        self.assertEqual(result['zip']['lng'], 22)

    def test_geocode_get_data__existent(self):
        """Testing geocode_get_data, with cached argument."""
        cg = CachedGeodata(key='20005', lat=111, lon=222, expires=time.time() + 10000)
        cg.save()
        result = geocode_get_data('20005')
        self.assertTrue('zip' in result)
        self.assertEqual(result['zip']['zipcode'], '20005')
        self.assertEqual(result['zip']['lat'], 111)
        self.assertEqual(result['zip']['lng'], 222)

    @patch('hud_api_replace.geocode.GoogleGeocode.google_maps_api')
    def test_geocode_get_data__expired(self, mock_geocode):
        """Testing geocode_get_data, with empty argument."""
        mock_geocode.return_value = {'result': ['20006', 11, 22]}
        cg = CachedGeodata(key='20006', lat=111, lon=222, expires=time.time() - 10000)
        cg.save()
        result = geocode_get_data('20006')
        self.assertEqual(result['zip']['zipcode'], '20006')
        self.assertEqual(result['zip']['lat'], 11)
        self.assertEqual(result['zip']['lng'], 22)
