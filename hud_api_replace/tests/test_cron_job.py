from django.test import TestCase
from hud_api_replace.management.commands import cron_job

class TestCronJob( TestCase ):
    def setUp( self ):
        self.cmd = cron_job.Command()
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}

# ---------- title_case ----------
    def test_title_case_1( self ):
        string = 'A lInE'
        self.assertEqual( self.cmd.title_case( string ), 'A Line' )


    def test_title_case_2( self ):
        string = 'a lInE'
        self.assertEqual( self.cmd.title_case( string ), 'A Line' )


    def test_title_case_3( self ):
        string = 'a lInE a LANE'
        self.assertEqual( self.cmd.title_case( string ), 'A Line a Lane' )


    def test_title_case_4( self ):
        string = 'as for THE IN noun'
        self.assertEqual( self.cmd.title_case( string ), 'As for the in Noun' )

# ---------- translate_languages ----------
    def test_translate_languages_1( self ):
        string = 'OTH'
        self.assertEqual( self.cmd.translate_languages( string ), 'Other')


    def test_translate_languages_2( self ):
        string = ''
        self.assertEqual( self.cmd.translate_languages( string ), '')


    def test_translate_languages_3( self ):
        string = 'EN'
        self.assertEqual( self.cmd.translate_languages( string ), 'English')


    def test_translate_languages_4( self ):
        string = 'TEST'
        self.assertEqual( self.cmd.translate_languages( string ), 'TEST')


    def test_translate_languages_5( self ):
        string = 'OTH,EN'
        self.assertEqual( self.cmd.translate_languages( string ), 'English, Other')


    def test_translate_languages_6( self ):
        string = 'SU,OTH,EN'
        self.assertEqual( self.cmd.translate_languages( string ), 'SU, English, Other')


    def test_translate_languages_2( self ):
        string = 'SU, OTH, EN'
        self.assertEqual( self.cmd.translate_languages( string ), 'SU, English, Other')

# ---------- translate_services ----------
    def test_translate_services_1( self ):
        string = 'OTH'
        self.assertEqual( self.cmd.translate_services( string ), 'Other')


    def test_translate_services_2( self ):
        string = ''
        self.assertEqual( self.cmd.translate_services( string ), 'Not available')


    def test_translate_services_3( self ):
        string = 'SRV'
        self.assertEqual( self.cmd.translate_services( string ), 'Service')


    def test_translate_services_4( self ):
        string = 'SRV1'
        self.assertEqual( self.cmd.translate_services( string ), 'SRV1')


    def test_translate_services_5( self ):
        string = 'OTH,   SRV'
        self.assertEqual( self.cmd.translate_services( string ), 'Other, Service')


    def test_translate_services_6( self ):
        string = 'OTH, SRV, SRV1'
        self.assertEqual( self.cmd.translate_services( string ), 'Other, Service, SRV1')

# ---------- reformat_weburl ----------
    def test_reformat_weburl_1( self ):
        url = 'www.google.com.com'
        self.assertEqual( self.cmd.reformat_weburl( url ), 'http://www.google.com.com')


    def test_reformat_weburl_2( self ):
        url = ''
        self.assertEqual( self.cmd.reformat_weburl( url ), 'Not available')



    def test_reformat_weburl_3( self ):
        url = 'http://www.com.com'
        self.assertEqual( self.cmd.reformat_weburl( url ), 'http://www.com.com')



    def test_reformat_weburl_4( self ):
        url = 'https://www.com.com'
        self.assertEqual( self.cmd.reformat_weburl( url ), 'https://www.com.com')

# ---------- reformat_email ----------
    def test_reformat_email_1( self ):
        email = ''
        self.assertEqual( self.cmd.reformat_email( email ), 'Not available')


    def test_reformat_email_2( self ):
        email = 'test@email.com'
        self.assertEqual( self.cmd.reformat_email( email ), 'test@email.com')


    def test_reformat_email_3( self ):
        email = 'test_email.com'
        self.assertEqual( self.cmd.reformat_email( email ), 'Not available')


    def test_reformat_email_2( self ):
        email = 'test@emailcom'
        self.assertEqual( self.cmd.reformat_email( email ), 'Not available')


    def test_reformat_email_5( self ):
        email = 'test@test@email.com'
        self.assertEqual( self.cmd.reformat_email( email ), 'Not available')

