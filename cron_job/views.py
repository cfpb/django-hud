# Create your views here.
from django.http import HttpResponse

import urllib2
import json
import re

from hud_api_replace.models import CounselingAgency


# Shamelessly copied most of hud-api-proxy.php
def title_case( string ):
    string.lower()
    str_list = string.split(' ')
    lower_case = ['a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with']
    for ndx, word in enumerate(str_list):
        if word not in lower_case:
            str_list[ndx] = word.title()

    return ' '.join(str_list)


def translate_languages( string ):
    languages = {
        " ":" ", "ASL":"ASL", "ARA":"Arabic", "CAM":"Cambodian", "CAN":"Cantonese", "CHI":"Chinese Mandarin",
        "CRE":"Creole", "CZE":"Czech", "ENG":"English", "FAR":"Farsi", "FRE":"French", "GER":"German",
        "HIN":"Hindi", "HMO":"Hmong", "IND":"Indonesian", "ITA":"Italian", "KOR":"Korean", "OTH":"Other",
        "POL":"Polish", "POR":"Portuguese", "RUS":"Russian", "SPA":"Spanish", "SWA":"Swahili", "TUR":"Turkish",
        "UKR":"Ukrainian", "VIE":"Vietnamese"}
    langs = string.split(',')
    verbose_languages = ''
    prepend = ''
    for lang in langs:
        verbose_languages += prepend + languages.get(lang, lang)
        prepend = ', '

    return verbose_languages


def translate_services( string ):
    services = { " ":" ",
        "FHW":"Fair Housing Pre-Purchase Education Workshops",
        "FBC":"Financial Management/Budget Counseling",
        "FBW":"Financial, Budgeting and Credit Repair Workshops",
        "HIC":"Home Improvement and Rehabilitation Counseling",
        "LM" :"Loss Mitigation",
        "MOI":"Marketing and Outreach Initiatives",
        "DRC":"Mobility and Relocation Counseling",
        "DFC":"Mortgage Delinquency and Default Resolution Counseling",
        "NDW":"Non-Delinquency Post Purchase Workshops",
        "PPC":"Pre-purchase Counseling",
        "PPW":"Pre-purchase Homebuyer Education Workshops",
        "PLW":"Predatory Lending Education Workshops",
        "RHC":"Rental Housing Counseling",
        "RHW":"Rental Housing Workshops",
        "DFW":"Resolving/Preventing Mortgage Delinquency Workshop",
        "RMC":"Reverse Mortgage Counseling",
        "HMC":"Services for Homeless Counseling",
    }
    srv_list = string.split(',')
    verbose_services = ''
    prepend = ''
    for srv in srv_list:
        verbose_services += prepend + services.get(srv, srv)
        prepend = ', '

    return verbose_services


def reformat_weburl( string ):
    string = string.strip()
    if string.find('.') == -1 or string.find('notavailable') != -1:
        return 'Not available'
    else:
        match = re.match(r'^http(s)?://', string)
        if not match:
            return 'http://' + string

    return string


def reformat_email( string ):
    string = string.strip()
    if string.find('.') == -1 or string.find('@') == -1:
        return 'Not available'

    return string


def sanitize_values( agcy ):
    # Change null values to ''
    # Apply proper letter case
    for key in agcy.keys():
        if agcy[key] == None:
            agcy[key] = ''

    agcy['nme'] = title_case( agcy['nme'] )
    agcy['city'] = title_case( agcy['city'] )
    agcy['mailingcity'] = title_case( agcy['mailingcity'] )

    agcy['languages'] = translate_languages( agcy['languages'] )
    agcy['services'] = translate_services( agcy['services'] )

    agcy['weburl'] = reformat_weburl( agcy['weburl'] )
    agcy['email'] = reformat_email( agcy['email'] )


def insert_agency( agcy ):
    sanitize_values( agcy )

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
        return

def load_hud_data( request ):
    # get data from HUD or show error message
    hud_api_url = "http://data.hud.gov/Housing_Counselor/searchByLocation"
    dc_lat = "38.8951"
    dc_long = "-77.0367"
    distance = "5000"

    try:
        response = urllib2.urlopen( "%s?Lat=%s&Long=%s&Distance=%s" % ( hud_api_url, dc_lat, dc_long, distance ) )
        data = json.loads( response.read() )
    except URLException as e:
        HttpResponse( e.reason )

    # delete from hud_api_replace_counselingagency
    CounselingAgency.objects.all().delete()

    # insert into it or show error message
    for agency in data:
        insert_agency( agency )

    return HttpResponse(' All data has been loaded ' + data[0]['adr1'])
