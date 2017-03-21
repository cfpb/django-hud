from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import json
import hmac
import base64
import hashlib
import geocoder
from geocoder.mapbox import Mapbox

import re
import time

from hud_api_replace.models import CachedGeodata



def _extract_zip_code(key):
    """What it says."""
    search = re.search('[0-9\-]*$', key)
    if search:
        key = search.group()
    return key


def geocode_get_data(address, zip_only=False):
    """Main function to obtain geocoding information."""
    address = str(address) + ", usa"
    try:
        cached = CachedGeodata.objects.all().filter(expires__gte=time.time()).get(key=address)
    except ObjectDoesNotExist:
        if zip_only:
            mb_result = Mapbox(address ,types='postcode')
            if mb_result.latlng:
                result = mb_result
            else:
                result = geocoder.osm(address)
        else:
            result = geocoder.mapbox(address)
        cached, created = CachedGeodata.objects.get_or_create(key=address)
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
