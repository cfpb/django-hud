from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Support for Python 2 and Python 3.
try:
    from urllib2 import urlopen, URLError
except ImportError:
    from urllib.error import URLError
    from urllib.request import urlopen

import json
import re
import hashlib
from functools import partial

from hud_api_replace.models import CounselingAgency, Language, Service
from hud_api_replace.geocode import PermanentMapbox

geocoder = partial(PermanentMapbox, country='us', types='address')

def needs_geocoding(sanitized):
    return (sanitized['agc_ADDR_LATITUDE'] is None
    or sanitized['agc_ADDR_LONGITUDE'] is None)

class Command(BaseCommand):
    help = 'Loads data from HUD into local hud_api_replace_counselingagency table.'
    # expect emails be a comma-separated list
    errors = ''
    languages = {}
    services = {}
    counselors = {}

    def handle(self, *args, **options):
        self.languages = self.convert2normal(self.hud_data('languages'))
        self.services = self.convert2normal(self.hud_data('services'))
        self.load_local_data()
        self.counselors = self.hud_data('counselors')
        self.save_data()
        self.stdout.write(self.errors)
        self.stdout.write('HUD data has been loaded.')

    def hud_data(self, step):
        """ Accesses HUD to get languages, services or counseling agency data """
        dc_lat = "38.8951"
        dc_long = "-77.0367"
        distance = "5000"
        urls = {
            'languages': 'http://data.hud.gov/Housing_Counselor/getLanguages',
            'services': 'http://data.hud.gov/Housing_Counselor/getServices',
            'counselors': "%s?Lat=%s&Long=%s&Distance=%s" %
                          ('http://data.hud.gov/Housing_Counselor/searchByLocation', dc_lat, dc_long, distance)
        }

        try:
            response = urlopen(urls[step])
            return json.loads(response.read())
        except URLError as e:
            self.errors += 'Error when accessing HUD server: %s\n' % e.reason
            return []
        except Exception as e:
            self.errors += 'Exception raised: %s\n' % e
            return []

    def convert2normal(self, storage):
        """ Populate self.services or self.languages """
        if storage:
            data = {}
            try:
                for obj in storage:
                    data[obj['key']] = obj['value']
                return data
            except Exception as e:
                self.errors += 'Exception raised: %s\n' % e
                return {}
        return {}

    def save_data(self):
        """ Save data to local database """
        if self.services:
            Service.objects.all().delete()
            for item in self.services:
                self.insert_lang_serv(Service(), [item, self.services[item]])
        if self.languages:
            Language.objects.all().delete()
            for item in self.languages:
                self.insert_lang_serv(Language(), [item, self.languages[item]])
        if self.counselors:

            for item in self.counselors:
                hasher = hashlib.sha256()
                normalized_json = json.dumps(item, sort_keys=True)
                hasher.update(normalized_json)
                counselor_hash = hasher.hexdigest()
                self.update_counselor(counselor_hash, item)
        else:
            self.errors += 'Error: there were no counselors returned from the HUD service'

    def load_local_data(self):
        """ Load langauges and/or services if call to HUD API didn't return them """
        if not self.languages:
            self.languages = self.convert2normal(self.convert2hud(Language.objects.all()))
        if not self.services:
            self.services = self.convert2normal(self.convert2hud(Service.objects.all()))
        return

    def convert2hud(self, data):
        """ HUD returned data has a very interesting structure,
            this function will convert its argument to that form """
        transformed_data = []
        try:
            for item in data:
                transformed_data.append({'key': item.abbr, 'value': item.name})
        except Exception:
            return []
        return transformed_data

    def insert_lang_serv(self, type_obj, item):
        """ Save a service/language to local database """
        try:
            type_obj.abbr = item[0]
            type_obj.name = item[1]
            type_obj.save()
        except Exception as e:
            if item and item[1]:
                self.errors += 'Error while saving [%s]: %s\n' % (item[1], e)
            else:
                self.errors += 'Error while saving: %s\n' % e

    def update_counselor(self, agc_hash, agc_data):
        """ Save a counseling agency to local database """
        self.sanitize_values(agc_data)
        counselor_id = agc_data.pop('agcid')
        manager = CounselingAgency.objects
        agency, created = manager.get_or_create(agcid = counselor_id,
                                                defaults = agc_data)
        if created:
            agency.source_data_hash = agc_hash
            agency.geocode_if_needed(geocoder)
        else:
            if (unicode(agc_hash) != agency.source_data_hash):
                agency.update(agc_data)
                agency.source_data_hash = agc_hash
                agency.save()
                
            agency.geocode_if_needed(geocoder)

    def sanitize_values(self, counselor):
        """ Change some fields so values have accepted letter case and/or values """
        # Change null values to ''
        # Apply proper letter case
        for key in counselor.keys():
            if counselor[key] is None:
                counselor[key] = ''

        counselor['nme'] = self.title_case(counselor['nme'])
        counselor['city'] = self.title_case(counselor['city'])
        counselor['mailingcity'] = self.title_case(counselor['mailingcity'])

        counselor['languages'] = self.translate_languages(counselor['languages'])
        counselor['services'] = self.translate_services(counselor['services'])

        counselor['weburl'] = self.reformat_weburl(counselor['weburl'])
        counselor['email'] = self.reformat_email(counselor['email'])

        if counselor['agc_ADDR_LATITUDE'] in ('', '0'):
            counselor['agc_ADDR_LATITUDE'] = None

        if counselor['agc_ADDR_LONGITUDE'] in ('', '0'):
            counselor['agc_ADDR_LONGITUDE'] = None

    # Shamelessly copied most of hud-api-proxy.php
    def title_case(self, string):
        """ Convert the argument to have title case """
        string = string.lower()
        str_list = string.split(' ')
        lower_case = ['a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with']
        str_list[0] = str_list[0].title()
        for ndx, word in enumerate(str_list):
            if word not in lower_case:
                str_list[ndx] = word.title()
        return ' '.join(str_list)

    def translate_languages(self, string):
        """ Change abbreviations for actual language names """
        langs = string.split(',')
        verbose_languages = ''
        prepend = ''
        other = ''
        for lang in langs:
            lang = lang.strip()
            if lang == 'OTH':
                other = 'Other'
            else:
                verbose_languages += prepend + self.languages.get(lang, lang)
                prepend = ', '
        if other:
            verbose_languages += prepend + other
        return verbose_languages

    def translate_services(self, string):
        """ Change abbreviations for actual service names """
        srv_list = string.split(',')
        verbose_services = ''
        prepend = ''
        for srv in srv_list:
            srv = srv.strip()
            verbose_services += prepend + self.services.get(srv, srv).replace(',', '&#44;')
            prepend = ', '

        if verbose_services == '':
            verbose_services = 'Not available'
        return verbose_services

    def reformat_weburl(self, string):
        """ Basic check of a url structure """
        string = string.strip()
        if string.find('.') == -1 or string.find('notavailable') != -1:
            return 'Not available'
        else:
            match = re.match(r'^http(s)?://', string)
            if not match:
                return 'http://' + string
        return string

    def reformat_email(self, string):
        """ Basic check of an email structure """
        string = string.strip()
        if string.find('.') == -1 or string.count('@') != 1:
            return 'Not available'
        return string
