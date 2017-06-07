from django.core.exceptions import ObjectDoesNotExist

from geocoder.mapbox import Mapbox, mapbox_access_token


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
