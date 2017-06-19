from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import geocoder
from geocoder.mapbox import Mapbox, mapbox_access_token

import re
import time

from hud_api_replace.models import CachedGeodata


class PermanentMapbox(Mapbox):
    def __init__(self, location, **kwargs):
        self.location = location
        self.url = u'https://api.mapbox.com/geocoding/v5/mapbox.places-permanent/{0}.json'.format(location)
        self.params = {
            'access_token': self._get_api_key(mapbox_access_token, **kwargs),
            'country': kwargs.get('country'),
            'proximity': self._get_proximity(),
            'types': kwargs.get('types'),
        }
        self._get_proximity(**kwargs)
        self._initialize(**kwargs)


def _extract_zip_code(key):
    """What it says."""
    search = re.search('[0-9\-]*$', key)
    if search:
        key = search.group()
    return key


def geocode_get_data(address, zip_only=False):
    """Main function to obtain geocoding information."""
    try:
        cached = CachedGeodata.objects.all().filter(expires__gte=time.time()).get(key=address)
    except ObjectDoesNotExist:
        if zip_only:
            mb_result = PermanentMapbox(address,
                                        types='postcode',
                                        country='us')
            result = mb_result
        else:
            result = PermanentMapbox(address, country='us')
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
