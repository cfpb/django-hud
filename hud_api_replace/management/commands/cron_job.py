from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage

import urllib2
import json
import re

from hud_api_replace.models import CounselingAgency, Language, Service


class Command( BaseCommand ):
    args = ''
    help = 'Loads data from HUD into local hud_api_replace_counselingagency table.'
    errors = ''
    notify_emails = [ 'test3@example.com' ]
    languages = {}
    services = {}

    def handle( self, *args, **options ):
        self.load_hud_data()
        if self.errors != '':
            email = EmailMessage('Errors while loading HUD data', self.errors, to = notify_emails)
            email.send()
        self.stdout.write('HUD data has been loaded.')


    def load_hud_data( self ):
        for step in ['languages', 'services', 'agencies']:
            data = self.hud_data( step )
            if not data and step != 'agencies':
                self.load_from_local_db( step )
            elif not data and step == 'agencies':
                return
            else:
                processed = self.process_data( step, data )
                self.save_data( step, processed )


    def process_data( self, step, data ):
        """ Generate a list of dicts """
        if step == 'agencies':
            return self.process_agc( data )
        elif step == 'languages':
            return self.process_lang_serv( self.languages, data )
        elif step == 'services':
            return self.process_lang_serv( self.services, data )
        else:
            self.errors += 'Unknown step [%s] in process_data' % step
            return []


    def process_lang_serv( self, storage, data ):
        """ Populate self.services or self.languages """
        for obj in data:
            storage[obj['key']] = obj['value']
        return storage


    def process_agc( self, data ):
        return data


    def save_data( self, step, data ):
        """ Save data to local db """
        if not data:
            return

        if step == 'agencies':
            self.save_agc( data )
        elif step == 'languages':
            self.save_lang_serv( step, data )
        elif step == 'services':
            self.save_lang_serv( step, data )
        else:
            self.errors += 'Unknown step [%s] in save_data' % step
            return


    def save_lang_serv( self, step, data ):
        """ Save Languages or Services to local DB """
        if step == 'services':
            Service.objects.all().delete()
            storage = self.services
        elif step == 'languages':
            Language.objects.all().delete()
            storage = self.languages
        else:
            self.errors += 'Unknown step [%s] in save_lang_serv' % step
            return

        for item in storage:
            self.insert_lang_serv( step, [item, storage[item]] )


    def save_agc( self, data ):
        """ Save Counseling Agency to DB """
        if data:
            # delete from hud_api_replace_counselingagency
            CounselingAgency.objects.all().delete()

            # save each agency from data
            for agency in data:
                self.insert_agency( agency )


    def load_from_local_db( self, step ):
        if step == 'services':
            storage = self.services
            data = Service.objects.all()
        elif step == 'languages':
            storage = self.languages
            data = Language.objects.all()
        else:
            self.errors += 'Unknown "step" [%s] in load_from_local_db' % step
            return

        for obj in data:
            storage[obj.abbr] = obj.name


    def hud_data( self, step ):
        """ Accesses HUD to read languages, services or counseling agency data """
        dc_lat = "38.8951"
        dc_long = "-77.0367"
        distance = "5000"
        urls = {
            'languages':'http://data.hud.gov/Housing_Counselor/getLanguages',
            'services':'http://data.hud.gov/Housing_Counselor/getServices',
            'agencies':"%s?Lat=%s&Long=%s&Distance=%s" %
                    ( 'http://data.hud.gov/Housing_Counselor/searchByLocation', dc_lat, dc_long, distance )
        }

        try:
            response = urllib2.urlopen( urls[step] )
            data = json.loads( response.read() )
        except urllib2.URLError as e:
            self.errors += 'Error when accessing HUD server: %s\n' % e.reason
            return []

        return data


    # Shamelessly copied most of hud-api-proxy.php
    def title_case( self, string ):
        string.lower()
        str_list = string.split(' ')
        lower_case = ['a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with']
        for ndx, word in enumerate(str_list):
            if word not in lower_case:
                str_list[ndx] = word.title()

        return ' '.join(str_list)


    def translate_languages( self, string ):
        langs = string.split(',')
        verbose_languages = ''
        prepend = ''
        other = ''
        for lang in langs:
            if lang == 'OTH':
                other = ', Other'
            else:
                verbose_languages += prepend + self.languages.get(lang, lang)
                prepend = ', '

        verbose_languages += other

        return verbose_languages


    def translate_services( self, string ):
        srv_list = string.split(',')
        verbose_services = ''
        prepend = ''
        for srv in srv_list:
            verbose_services += prepend + self.services.get(srv, srv)
            prepend = ', '

        if verbose_services == '':
            verbose_services = 'Not available'

        return verbose_services


    def reformat_weburl( self, string ):
        string = string.strip()
        if string.find('.') == -1 or string.find('notavailable') != -1:
            return 'Not available'
        else:
            match = re.match(r'^http(s)?://', string)
            if not match:
                return 'http://' + string

        return string


    def reformat_email( self, string ):
        string = string.strip()
        if string.find('.') == -1 or string.find('@') == -1:
            return 'Not available'

        return string


    def sanitize_values( self, agcy ):
        # Change null values to ''
        # Apply proper letter case
        for key in agcy.keys():
            if agcy[key] == None:
                agcy[key] = ''

        agcy['nme'] = self.title_case( agcy['nme'] )
        agcy['city'] = self.title_case( agcy['city'] )
        agcy['mailingcity'] = self.title_case( agcy['mailingcity'] )

        agcy['languages'] = self.translate_languages( agcy['languages'] )
        agcy['services'] = self.translate_services( agcy['services'] )

        agcy['weburl'] = self.reformat_weburl( agcy['weburl'] )
        agcy['email'] = self.reformat_email( agcy['email'] )


    def insert_lang_serv( self, step, data ):
        if step == 'services':
            obj = Service()
        elif step == 'languages':
            obj = Language()
        else:
            self.errors += 'Unknown step [%s] in insert_lang_serv' % step
            return

        obj.abbr = data[0]
        obj.name = data[1]
        try:
            obj.save()
        except Exception as e:
            self.errors += 'Error while saving %s [%s]: %s\n' % ( step, obj.name, e )
            return


    def insert_agency( self, agcy ):
        self.sanitize_values( agcy )

        obj = CounselingAgency()
        obj.agcid = agcy.get('agcid', '')
        obj.adr1 = agcy.get('adr1', '')
        obj.adr2 = agcy.get('adr2', '')
        obj.city = agcy.get('city', '')
        obj.email = agcy.get('email', '')
        obj.fax = agcy.get('fax', '')
        obj.nme = agcy.get('nme', '')
        obj.phone1 = agcy.get('phone1', '')
        obj.statecd = agcy.get('statecd', '')
        obj.weburl = agcy.get('weburl', '')
        obj.zipcd = agcy.get('zipcd', '')
        obj.agc_ADDR_LATITUDE = agcy.get('agc_ADDR_LATITUDE', '')
        obj.agc_ADDR_LONGITUDE = agcy.get('agc_ADDR_LONGITUDE', '')
        obj.languages = agcy.get('languages', '')
        obj.services = agcy.get('services', '')
        obj.parentid = agcy.get('parentid', '')
        obj.county_NME = agcy.get('county_NME', '')
        obj.phone2 = agcy.get('phone2', '')
        obj.mailingadr1 = agcy.get('mailingadr1', '')
        obj.mailingadr2 = agcy.get('mailingadr2', '')
        obj.mailingcity = agcy.get('mailingcity', '')
        obj.mailingzipcd = agcy.get('mailingzipcd', '')
        obj.mailingstatecd = agcy.get('mailingstatecd', '')
        obj.state_NME = agcy.get('state_NME', '')
        obj.state_FIPS_CODE = agcy.get('state_FIPS_CODE', '')
        obj.faithbased = agcy.get('faithbased', '')
        obj.colonias_IND = agcy.get('colonias_IND', '')
        obj.migrantwkrs_IND = agcy.get('migrantwkrs_IND', '')
        obj.agc_STATUS = agcy.get('agc_STATUS', '')
        obj.agc_SRC_CD = agcy.get('agc_SRC_CD', '')
        obj.counslg_METHOD = agcy.get('counslg_METHOD', '')
        try:
            obj.save()
        except Exception as e:
            # email somebody about the error
            self.errors += 'Error while saving agency [%s]: %s\n' % ( obj.nme, e )
            return
