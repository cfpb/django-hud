from django.test import TestCase
from mock import MagicMock, patch

from hud_api_replace.geocode import GoogleGeocode

class TestGoogleGeocode( TestCase ):
    def setUp( self ):
        self.gc = GoogleGeocode( 20005 )

    def test_init( self ):
        """ Testing __init__ """
        self.assertEqual( self.gc.zipcode, 20005 )
        self.assertEqual( type(self.gc.invisible_zipcodes), dict )
        self.assertTrue( len(self.gc.invisible_zipcodes) > 0 )
        self.assertTrue( self.gc.privateKey != None )
        self.assertTrue( self.gc.clientID != None )

    def test_is_usa_or_territory__correct( self ):
        """ Testing is_usa_or_territory, GUAM, USVI, ASamoa, PRico, Cnmi, Rmi, Usa """
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, GUAM something else" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, UsVi" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, American Samoa else" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, Puerto Rico something else" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, Cnmi" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, rmi" ))
        self.assertTrue( self.gc.is_usa_or_territory( "123 Address, Usa" ))

    def test_is_usa_or_territory__wrong( self ):
        """ Testing is_usa_or_territory, Not USA address """
        self.assertFalse( self.gc.is_usa_or_territory( "123 Address, Mexico City, Mexico" ))

    def test_signed_url__correct( self ):
        """ Testing signed_url, correct url """
        url = "http://maps.googleapis.com/maps/api/geocode/json?address=New+York&sensor=false&client=clientID"
        expected = "http://maps.googleapis.com/maps/api/geocode/json?address=New+York&sensor=false&client=clientID&signature=KrU1TzVQM7Ur0i8i7K3huiw3MsA="
        self.gc.privateKey = "vNIXE0xscrmjlyV-12Nj_BvUPaw="
        self.gc.clientID = "clientID"
        signed_url = self.gc.signed_url( url )
        self.assertEqual( signed_url, expected )

    def test_signed_url__empty( self ):
        """ Testing signed_url, empty url """
        url = ''
        signed_url = self.gc.signed_url( url )
        self.assertEqual( signed_url, None )

    @patch('urllib2.urlopen')
    def test_request_google_maps( self, mock_urlopen ):
        """ Testing request_google_maps """
        def urlopen_check_param( param ):
            self.param = param
            mm = MagicMock()
            mm.read.return_value = '{"Success":"success"}'
            return mm

        mock_urlopen.side_effect = urlopen_check_param
        expected = "http://maps.googleapis.com/maps/api/geocode/json?address=20005&sensor=false&client=" + self.gc.clientID
        response = self.gc.request_google_maps( 20005 )
        self.assertTrue( expected in self.param )
        self.assertEqual( response['Success'], 'success' )

    def test_google_maps_api( self ):
        pass


