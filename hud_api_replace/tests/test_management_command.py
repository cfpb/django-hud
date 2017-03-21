from django.test import TestCase
from mock import MagicMock, patch

# Support for Python 2 and Python 3.
try:
    from urllib2 import URLError
except ImportError:
    from urllib.error import URLError

from hud_api_replace.management.commands import load_hud_data
from hud_api_replace.models import Service, Language, CounselingAgency


def hud_api_urls(step):
    urls = {
        'languages': 'http://data.hud.gov/Housing_Counselor/getLanguages',
        'services': 'http://data.hud.gov/Housing_Counselor/getServices',
        'counselors': 'http://data.hud.gov/Housing_Counselor/searchByLocation',
    }

    if step in urls:
        return urls[step]
    else:
        return None


class SimpleClass(object):
    def __init__(self, abbr, name):
        self.abbr = abbr
        self.name = name


class TestCronJob(TestCase):
    def setUp(self):
        self.cmd = load_hud_data.Command()

    def test_handle(self):
        # not really necessary
        pass

    @patch('hud_api_replace.management.commands.load_hud_data.urlopen')
    def test_hud_data__steps(self, mock_urlopen):
        """ Testing hud_data, step = [services|languages|counselors] """

        def hud_data_return_param(param):
            mm = MagicMock()
            mm.read.return_value = '{"Success":"success","Access_URL":"%s"}' % param
            return mm

        mock_urlopen.side_effect = hud_data_return_param
        response = self.cmd.hud_data('services')
        self.assertTrue(response['Access_URL'] == hud_api_urls('services'))
        self.assertTrue(response['Success'] == 'success')
        response = self.cmd.hud_data('languages')
        self.assertTrue(response['Access_URL'] == hud_api_urls('languages'))
        self.assertTrue(response['Success'] == 'success')
        response = self.cmd.hud_data('counselors')
        self.assertTrue(response['Access_URL'].startswith(hud_api_urls('counselors')))
        self.assertTrue(response['Success'] == 'success')

    @patch('hud_api_replace.management.commands.load_hud_data.urlopen')
    def test_hud_data__error(self, mock_urlopen):
        """ Testing hud_data, raise a URLError exception """
        mock_urlopen.side_effect = URLError('URLError exception')
        response = self.cmd.hud_data('services')
        self.assertTrue('URLError exception' in self.cmd.errors)
        self.assertTrue(response == [])

    @patch('hud_api_replace.management.commands.load_hud_data.urlopen')
    def test_hud_data__bad_json(self, mock_urlopen):
        """ Testing hd_data, return bad json from urllib2.urlopen """
        mm = MagicMock()
        mm.read.return_value = "{'Success': 'success'}"
        mock_urlopen.return_value = mm
        response = self.cmd.hud_data('services')
        self.assertTrue('Exception raised' in self.cmd.errors)
        self.assertTrue(response == [])

    def test_convert2normal__empty(self):
        """ Testing convert2normal, empty list """
        response = self.cmd.convert2normal({})
        self.assertTrue(response == {})

    def test_convert2normal__none(self):
        """ Testing convert2normal, None """
        response = self.cmd.convert2normal(None)
        self.assertTrue(response == {})

    def test_convert2normal__list(self):
        """ Testing convert2normal, list of the correct form """
        data = [{'key': 'key1', 'value': 'value1'}, {'key': 'key2', 'value': 'value2'}]
        response = self.cmd.convert2normal(data)
        self.assertTrue(len(response) == 2)
        self.assertTrue('key1' in response)
        self.assertTrue('key2' in response)
        self.assertTrue(response['key1'] == 'value1')
        self.assertTrue(response['key2'] == 'value2')

    def test_convert2normal__wrong_list(self):
        """ Testing convert2normal, list of the wrong form """
        data = {'key1': 'value1', 'key2': 'value2'}
        response = self.cmd.convert2normal(data)
        self.assertTrue(response == {})
        self.assertTrue('Exception raised' in self.cmd.errors)

    def test_save_data__services(self):
        """ Testing save_data, only self.services is set """
        self.cmd.services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        self.cmd.save_data()
        services = Service.objects.all()
        languages = Language.objects.all()
        counselors = CounselingAgency.objects.all()
        abbr2 = services.filter(abbr__exact='Abbr2')[0]
        self.assertTrue('there were no counselors' in self.cmd.errors)
        self.assertTrue(len(services) == 2)
        self.assertTrue(len(languages) == 0)
        self.assertTrue(len(counselors) == 0)
        self.assertTrue(abbr2.name == 'Service 2')

    def test_save_data__services_languages(self):
        """ Testing save_data, self.services and self.languages are set """
        self.cmd.services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        self.cmd.languages = {'Lang1': 'Language 1', 'Lang2': 'Language 2', 'Lang3': 'Language 3'}
        self.cmd.save_data()
        services = Service.objects.all()
        languages = Language.objects.all()
        counselors = CounselingAgency.objects.all()
        abbr2 = services.filter(abbr__exact='Abbr2')[0]
        lang3 = languages.filter(abbr__exact='Lang3')[0]
        self.assertTrue('there were no counselors' in self.cmd.errors)
        self.assertTrue(len(services) == 2)
        self.assertTrue(len(languages) == 3)
        self.assertTrue(len(counselors) == 0)
        self.assertTrue(abbr2.name == 'Service 2')
        self.assertTrue(lang3.name == 'Language 3')

    def test_load_local_data__languages(self):
        """ Testing load_local_data, languages is set """
        services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        languages = {'Lang1': 'Language 1', 'Lang2': 'Language 2', 'Lang3': 'Language 3'}
        self.cmd.languages = languages
        self.cmd.services = services
        self.cmd.save_data()
        self.cmd.services = None
        self.cmd.languages['Lang4'] = 'Language 4'
        self.cmd.load_local_data()
        self.assertTrue(len(self.cmd.languages) == 4)
        self.assertTrue('Lang4' in self.cmd.languages)
        self.assertTrue(len(self.cmd.services) == 2)

    def test_load_local_data__services(self):
        """ Testing load_local_data, services is set """
        services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        languages = {'Lang1': 'Language 1', 'Lang2': 'Language 2', 'Lang3': 'Language 3'}
        self.cmd.languages = languages
        self.cmd.services = services
        self.cmd.save_data()
        self.cmd.languages = None
        self.cmd.services['Abbr3'] = 'Service 3'
        self.cmd.load_local_data()
        self.assertTrue(len(self.cmd.services) == 3)
        self.assertTrue('Abbr3' in self.cmd.services)
        self.assertTrue(len(self.cmd.languages) == 3)

    def test_load_local_data__both(self):
        """ Testing load_local_data, services and languages are set """
        services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        languages = {'Lang1': 'Language 1', 'Lang2': 'Language 2', 'Lang3': 'Language 3'}
        self.cmd.languages = languages
        self.cmd.services = services
        self.cmd.save_data()
        self.cmd.languages['Lang4'] = 'Language 4'
        self.cmd.services['Abbr3'] = 'Service 3'
        self.cmd.load_local_data()
        self.assertTrue(len(self.cmd.services) == 3)
        self.assertTrue('Abbr3' in self.cmd.services)
        self.assertTrue(len(self.cmd.languages) == 4)
        self.assertTrue('Lang4' in self.cmd.languages)

    def test_load_local_data__none(self):
        """ Testing load_local_data, none are set """
        services = {'Abbr1': 'Service 1', 'Abbr2': 'Service 2'}
        languages = {'Lang1': 'Language 1', 'Lang2': 'Language 2', 'Lang3': 'Language 3'}
        self.cmd.languages = languages
        self.cmd.services = services
        self.cmd.save_data()
        self.cmd.languages = None
        self.cmd.services = None
        self.cmd.load_local_data()
        self.assertTrue(len(self.cmd.services) == 2)
        self.assertFalse('Abbr3' in self.cmd.services)
        self.assertTrue('Abbr2' in self.cmd.services)
        self.assertTrue(len(self.cmd.languages) == 3)
        self.assertFalse('Lang4' in self.cmd.languages)
        self.assertTrue('Lang3' in self.cmd.languages)

    def test_convert2hud__empty(self):
        """ Testing convert2hud, empty list """
        response = self.cmd.convert2hud([])
        self.assertTrue(response == [])

    def test_convert2hud__none(self):
        """ Testing convert2hud, None """
        response = self.cmd.convert2hud(None)
        self.assertTrue(response == [])

    def test_convert2hud__list(self):
        """ Testing convert2hud, list in the correct form """
        data = [SimpleClass('Abbr1', 'Name1'), SimpleClass('Abbr2', 'Name2')]
        response = self.cmd.convert2hud(data)
        self.assertTrue(len(response) == 2)
        self.assertTrue(response[0]['key'] == 'Abbr1')
        self.assertTrue(response[0]['value'] == 'Name1')

    def test_convert2hud__wrong_list(self):
        """ Testing convert2hud, list in the wrong form """
        data = [1, 2, 3]
        response = self.cmd.convert2hud(data)
        self.assertTrue(response == [])

    def test_insert_lang_serv__service(self):
        """ Testing insert_lang_serv, service data """
        service = ['Abbr1', 'Service 1']
        self.cmd.insert_lang_serv(Service(), service)
        obj = Service.objects.get(abbr__exact='Abbr1')
        self.assertTrue(obj.name == 'Service 1')

    def test_insert_lang_serv__language(self):
        """ Testing insert_lang_serv, language data """
        language = ['Lang1', 'Language 1']
        self.cmd.insert_lang_serv(Language(), language)
        obj = Language.objects.get(abbr__exact='Lang1')
        self.assertTrue(obj.name == 'Language 1')

    def test_insert_lang_serv__none(self):
        """ Testing insert_lang_serv, None """
        self.cmd.insert_lang_serv(Language(), None)
        self.assertTrue('Error while saving' in self.cmd.errors)

    def test_insert_lang_serv__empty(self):
        """ Testing insert_lang_serv, empty list """
        self.cmd.insert_lang_serv(Language(), [])
        self.assertTrue('Error while saving' in self.cmd.errors)

    def test_insert_counselor__empty(self):
        """ Testing insert_counselor, empty dict """
        self.cmd.insert_counselor({})
        objs = CounselingAgency.objects.all()
        self.assertTrue(len(objs) == 0)

    def test_insert_counselor__none(self):
        """ Testing insert_counselor, None """
        self.cmd.insert_counselor(None)
        objs = CounselingAgency.objects.all()
        self.assertTrue(len(objs) == 0)

    def test_sanitize_values__key(self):
        """ Testing sanitize_values, key == None """
        counselor = {
            'agcid': None, 'nme': None, 'languages': 'OTH,EN', 'services': 'SRV,SRV2',
            'weburl': 'www.agc1.com', 'agc_ADDR_LATITUDE': '', 'agc_ADDR_LONGITUDE': '0',
            'email': 'test@example.com', 'city': 'City 1', 'mailingcity': 'City 1'
        }
        self.cmd.sanitize_values(counselor)
        self.assertTrue(counselor['agcid'] == '')
        self.assertTrue(counselor['nme'] == '')

    def test_sanitize_values__agc_latitude_0(self):
        """ Testing sanitize_values, agc_ADDR_LATITUDE = '' """
        counselor = {
            'agcid': None, 'nme': None, 'languages': 'OTH,EN', 'services': 'SRV,SRV2',
            'weburl': 'www.agc1.com', 'agc_ADDR_LATITUDE': '', 'agc_ADDR_LONGITUDE': '0',
            'email': 'test@example.com', 'city': 'City 1', 'mailingcity': 'City 1'
        }
        self.cmd.sanitize_values(counselor)
        self.assertTrue(counselor['agc_ADDR_LATITUDE'] == '0')

    def test_sanitize_values__agc_latitude_1(self):
        """ Testing sanitize_values, agc_ADDR_LATITUDE = None """
        counselor = {
            'agcid': None, 'nme': None, 'languages': 'OTH,EN', 'services': 'SRV,SRV2',
            'weburl': 'www.agc1.com', 'agc_ADDR_LATITUDE': None, 'agc_ADDR_LONGITUDE': '0',
            'email': 'test@example.com', 'city': 'City 1', 'mailingcity': 'City 1'
        }
        self.cmd.sanitize_values(counselor)
        self.assertTrue(counselor['agc_ADDR_LATITUDE'] == '0')

    def test_sanitize_values__agc_longitude_0(self):
        """ Testing sanitize_values, agc_ADDR_LONGITUDE = '' """
        counselor = {
            'agcid': None, 'nme': None, 'languages': 'OTH,EN', 'services': 'SRV,SRV2',
            'weburl': 'www.agc1.com', 'agc_ADDR_LATITUDE': None, 'agc_ADDR_LONGITUDE': '',
            'email': 'test@example.com', 'city': 'City 1', 'mailingcity': 'City 1'
        }
        self.cmd.sanitize_values(counselor)
        self.assertTrue(counselor['agc_ADDR_LONGITUDE'] == '0')

    def test_sanitize_values__agc_longitude_1(self):
        """ Testing sanitize_values, agc_ADDR_LONGITUDE = None """
        counselor = {
            'agcid': None, 'nme': None, 'languages': 'OTH,EN', 'services': 'SRV,SRV2',
            'weburl': 'www.agc1.com', 'agc_ADDR_LATITUDE': None, 'agc_ADDR_LONGITUDE': None,
            'email': 'test@example.com', 'city': 'City 1', 'mailingcity': 'City 1'
        }
        self.cmd.sanitize_values(counselor)
        self.assertTrue(counselor['agc_ADDR_LONGITUDE'] == '0')

    def test_title_case_1(self):
        """ Testing title_case, A lInE """
        string = 'A lInE'
        self.assertEqual(self.cmd.title_case(string), 'A Line')

    def test_title_case_2(self):
        """ Testing title_case, a lInE """
        string = 'a lInE'
        self.assertEqual(self.cmd.title_case(string), 'A Line')

    def test_title_case_3(self):
        """ Testing title_case, a lInE a LANE """
        string = 'a lInE a LANE'
        self.assertEqual(self.cmd.title_case(string), 'A Line a Lane')

    def test_title_case_4(self):
        """ Testing title_case, as for THE IN noun """
        string = 'as for THE IN noun'
        self.assertEqual(self.cmd.title_case(string), 'As for the in Noun')

    def test_translate_languages_oth(self):
        """ Testing translate_languages, OTH """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'OTH'
        self.assertEqual(self.cmd.translate_languages(string), 'Other')

    def test_translate_languages_empty(self):
        """ Testing translate_languages, empty string """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = ''
        self.assertEqual(self.cmd.translate_languages(string), '')

    def test_translate_languages_en(self):
        """ Testing translate_languages, EN """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'EN'
        self.assertEqual(self.cmd.translate_languages(string), 'English')

    def test_translate_languages_inexistent_code(self):
        """ Testing translate_languages, TEST """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'TEST'
        self.assertEqual(self.cmd.translate_languages(string), 'TEST')

    def test_translate_languages_two_codes(self):
        """ Testing translate_languages, OTH,EN """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'OTH,EN'
        self.assertEqual(self.cmd.translate_languages(string), 'English, Other')

    def test_translate_languages_several_codes_one_inexsitent(self):
        """ Testing translate_languages, SU,OTH,EN """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'SU,OTH,EN'
        self.assertEqual(self.cmd.translate_languages(string), 'SU, English, Other')

    def test_translate_languages_with_spaces(self):
        """ Testing translate_languages, with spaces SU, OTH , EN """
        self.cmd.languages = {'OTH': 'Other', '': '', 'EN': 'English'}
        string = 'SU, OTH, EN'
        self.assertEqual(self.cmd.translate_languages(string), 'SU, English, Other')

    def test_translate_services_oth(self):
        """ Testing translate_services, OTH """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = 'OTH'
        self.assertEqual(self.cmd.translate_services(string), 'Other')

    def test_translate_services_empty(self):
        """ Testing translate_services, empty string """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = ''
        self.assertEqual(self.cmd.translate_services(string), 'Not available')

    def test_translate_services_srv(self):
        """ Testing translate_services, SRV """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = 'SRV'
        self.assertEqual(self.cmd.translate_services(string), 'Service')

    def test_translate_services_inexistent_code(self):
        """ Testing translate_services, SRV1 """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = 'SRV1'
        self.assertEqual(self.cmd.translate_services(string), 'SRV1')

    def test_translate_services_several_with_spaces(self):
        """ Testing translate_services, with spaces OTH,  SRV """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = 'OTH,   SRV '
        self.assertEqual(self.cmd.translate_services(string), 'Other, Service')

    def test_translate_services_several_one_inexistent(self):
        """ Testing translate_services, OTH, SRV, SRV1 """
        self.cmd.services = {'OTH': 'Other', '': '', 'SRV': 'Service'}
        string = 'OTH, SRV , SRV1'
        self.assertEqual(self.cmd.translate_services(string), 'Other, Service, SRV1')

    def test_reformat_weburl_1(self):
        """ Testing reformat_weburl, no http """
        url = 'www.google.com.com'
        self.assertEqual(self.cmd.reformat_weburl(url), 'http://www.google.com.com')

    def test_reformat_weburl_2(self):
        """ Testing reformat_url, empty string """
        url = ''
        self.assertEqual(self.cmd.reformat_weburl(url), 'Not available')

    def test_reformat_weburl_3(self):
        """ Testing reformat_url, nothing to change """
        url = 'http://www.com.com'
        self.assertEqual(self.cmd.reformat_weburl(url), 'http://www.com.com')

    def test_reformat_weburl_4(self):
        """ Testing reformat_url, https """
        url = 'https://www.com.com'
        self.assertEqual(self.cmd.reformat_weburl(url), 'https://www.com.com')

    def test_reformat_email_1(self):
        """ Testing reformat_email, empty string """
        email = ''
        self.assertEqual(self.cmd.reformat_email(email), 'Not available')

    def test_reformat_email_2(self):
        """ Testing reformat_email, good email """
        email = 'test@example.com'
        self.assertEqual(self.cmd.reformat_email(email), 'test@example.com')

    def test_reformat_email_3(self):
        """ Testing reformat_email, no @ sign """
        email = 'test_example.com'
        self.assertEqual(self.cmd.reformat_email(email), 'Not available')

    def test_reformat_email_4(self):
        """ Testing reformat_email, no . after @ sign """
        email = 'test@examplecom'
        self.assertEqual(self.cmd.reformat_email(email), 'Not available')

    def test_reformat_email_5(self):
        """ Testing reformat_email, 2 @ signs """
        email = 'test@test@example.com'
        self.assertEqual(self.cmd.reformat_email(email), 'Not available')
