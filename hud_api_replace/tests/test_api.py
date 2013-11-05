from django.test import TestCase, Client
from hud_api_replace.models import CounselingAgency, Language, Service

class TestAPI( TestCase ):
    """ Need to use django.test.client """

    """ add these later, when figured how to work with mock """
