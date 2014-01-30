from django.conf import settings

import urllib2
import json
import urlparse
import hmac
import base64
import hashlib


class GoogleGeocode(object):

    def __init__(self, zipcode):
        self.zipcode = zipcode
        self.privateKey = settings.GOOGLE_MAPS_API_PRIVATE_KEY
        self.clientID = settings.GOOGLE_MAPS_API_CLIENT_ID
        # Google doesn't return any information for some postal codes for US Territories in the Pacific,
        #  we'll get geocoding info for other postal codes which are located relatively close to the original
        #  ones.
        self.invisible_zipcodes = {
            # Federated States of Micronesia
            '96941': 96960,
            '96942': 96960,
            '96943': 96960,
            '96944': 96960,
            # Marshall Islands
            '96970': 96960,
            # North Mariana Islands
            '96951': 96950,
            '96952': 96950,
            # Palau
            '96940': 96910,
            # Guam
            '96912': 96910,
            '96916': 96915,
            '96917': 96915,
            '96919': 96915,
            '96921': 96915,
            '96923': 96929,
            '96928': 96929,
            '96931': 96929,
            '96932': 96929,
        }

    def is_usa_or_territory(self, formatted_address):
        """ See whether argument is an address in the USA or one of the territories we're interested in """
        import re
        # a somewhat full list of territories and zip codes
        # http://en.m.18dao.net/ZIP_Code/United_States_External_Territories
        territories = [
            'guam',             # Guam
            'usvi',             # US Virgin Islands
            'american samoa',   # American Samoa
            'puerto rico',      # Puerto Rico
            'cnmi',             # North Mariana Islands
            'rmi',              # Marshall Islands
            'usa',
        ]
        joined = '|'.join(territories)
        return re.search(joined, formatted_address.lower())

    def signed_url(self, url):
        """ Google Maps API requires signature parameter, this function generates it and returns the new url
        see example on https://developers.google.com/maps/documentation/business/webservices/auth """
        if not url or url == '':
            return
        parsed = urlparse.urlparse(url)
        urlToSign = parsed.path + "?" + parsed.query
        decodedKey = base64.urlsafe_b64decode(self.privateKey)
        signature = hmac.new(decodedKey, urlToSign, hashlib.sha1)
        encodedSignature = base64.urlsafe_b64encode(signature.digest())
        return url + '&signature=' + encodedSignature

    def request_google_maps(self, zipcode):
        """ Access Google Maps API to obtain zipcode geocoding information """
        url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % zipcode
        url += '&client=' + self.clientID
        url = self.signed_url(url)
        response = urllib2.urlopen(url)
        return json.loads(response.read())

    def google_maps_api(self):
        """ Get geocoding info for zipcode """
        try:
            jsongeocode = self.request_google_maps(self.zipcode)
            if jsongeocode['status'] == 'ZERO_RESULTS' and self.zipcode in self.invisible_zipcodes:
                jsongeocode = self.request_google_maps(self.invisible_zipcodes[self.zipcode])
            for result in jsongeocode['results']:
                if self.is_usa_or_territory(result['formatted_address']):
                    if result['geometry']:
                        lat = result['geometry']['location']['lat']
                        lng = result['geometry']['location']['lng']
                        return {'zip': {
                            'zipcode': self.zipcode,
                            'lat': lat,
                            'lng': lng,
                        }}
        except KeyError as e:
            return {'error': 'Environmental variables GOOGLE_MAPS_API_PRIVATE_KEY and GOOGLE_MAPS_API_CLIENT_ID must be set'}
        except:
            return {'error': 'Error while getting geocoding information for ' + self.zipcode}
        return {'error': 'No data was returned from Google'}
