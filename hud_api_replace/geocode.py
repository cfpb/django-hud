from django.conf import settings

import urllib2
import json
import urlparse
import hmac
import base64
import hashlib
import geocoder

# This library has some issues when parsing addresses, esp. those with suite/apt #s.
#  which results in weird looking keys. I can live with that, we only need zipcode
#  parsed correctly  so we can use it to call GoogleGeocode.
from address import AddressParser
import re
import time

from hud_api_replace.models import CachedGeodata


def _geocode_compute_key(address):
    """Generate a key out of <address>."""
    if address == '' or re.match('^[0-9]{5}(-[0-9]{4})?$', str(address)):
        return address
    try:
        ap = AddressParser()
        addr = ap.parse_address(address)
        street = '%s %s %s %s' % (addr.house_number, addr.street_prefix, addr.street, addr.street_suffix)
        citystate = '%s,%s' % (addr.city, addr.state)
        # address lib doesn't handle xxxxx-xxxx zip codes
        search = re.search('([0-9]{5})-[0-9]{4}$', address)
        if search:
            addr.zip = search.groups()[0]
        return '%s|%s|%s' % (street.upper(), citystate.upper(), addr.zip)
    except:
        return ''


def _extract_zip_code(key):
    """What it says."""
    search = re.search('[0-9\-]*$', key)
    if search:
        key = search.group()
    return key


def _geocode_cached_data(key):
    """Returns data stored for <key>."""
    try:
        result = CachedGeodata.objects.all().get(key=key).filter(expires__gte=time.time())
        return result
    except:
        raise Exception('No cached data found for %s', key)



def geocode_get_data(address):
    """Main function to obtain geocoding information."""
    try:
        key = _geocode_compute_key(address)
        cached = _geocode_cached_data(key)
    except:
        # apparently _geocode_cached_data raised an Exception
        result = geocoder.mapbox(address)
        cached, created = CachedGeodata.objects.get_or_create(key=key)
        cached.lat = result.lat
        cached.lon = result.lng
        # 1728000 is 20 days
        cached.expires = int(time.time()) + getattr(settings, 'DJANGO_HUD_GEODATA_EXPIRATION_INTERVAL', 1728000)
        cached.save()

    return {'zip': {
            'zipcode': address,
            'lat': cached.lat,
            'lng': cached.lon,
            }}
