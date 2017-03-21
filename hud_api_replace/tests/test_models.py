from django.test import TestCase
from hud_api_replace.models import CounselingAgency, Language, Service


class TestModels(TestCase):
    def test_counseling_agency(self):
        ca = CounselingAgency(nme='Test', agcid=1)
        self.assertEqual(str(ca), 'Test')

    def test_language(self):
        lng = Language(name='English')
        self.assertEqual(str(lng), 'English')

    def test_service(self):
        srv = Service(name='Service')
        self.assertEqual(str(srv), 'Service')
