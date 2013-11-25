from django.conf import settings

# import dstk
import urllib2
import json
import urlparse
import hmac, base64, hashlib

class GeoCode( object ):

    def __init__( self, zipcode ):
       self.zipcode = zipcode
       self.privateKey = settings.GOOGLE_MAPS_API_PRIVATE_KEY
       self.clientID = settings.GOOGLE_MAPS_API_CLIENT_ID

    def is_usa_or_territory( self, formatted_address ):
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
        joined = '|'.join( territories )
        return re.search( joined, formatted_address.lower() )


    def signed_url( self, url ):
        """ Google Maps API requires signature parameter, this function generates it and returns the new url
        see example on https://developers.google.com/maps/documentation/business/webservices/auth """
        parsed = urlparse.urlparse( url )
        urlToSign = parsed.path + "?" + parsed.query
        decodedKey = base64.urlsafe_b64decode( self.privateKey )
        signature = hmac.new( decodedKey, urlToSign, hashlib.sha1 )
        encodedSignature = base64.urlsafe_b64encode( signature.digest() )
        return url + '&signature=' + encodedSignature


    def google_maps_api( self ):
        """ Google API """
        address = self.zipcode
        url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % address
        try:
            url += '&client=' + self.clientID
            url = self.signed_url( url )
            response = urllib2.urlopen( url )
            jsongeocode = json.loads( response.read() )
            for result in jsongeocode['results']:
                if 'postal_code' in result['types'] and self.is_usa_or_territory(result['formatted_address']):
                    if result['geometry']:
                        lat = result['geometry']['location']['lat']
                        lng = result['geometry']['location']['lng']
                        return { 'zip': {
                            'zipcode': self.zipcode,
                            'lat': lat,
                            'lng': lng,
                        }}
        except KeyError as e:
            return {'error': 'Environmental variables GOOGLE_MAPS_API_PRIVATE_KEY and GOOGLE_MAPS_API_CLIENT_ID must be set'}
        except:
            return {'error': 'Error while getting geocoding information for ' + self.zipcode}
        return {'error': 'No data was returned from Google'}


    def dstk_api( self ):
        # dstk = dstk.DSTK( {'apiBase': 'http://dstk.address.com'} )
        # or set DSTK_API_BASE env variable
        # by default connects to http://datasciencetoolkit.org
        dst = dstk.DSTK()
        address = self.zipcode + ', US'
        data = dst.street2coordinates( [address] )
        if isinstance( data[address], dict ):
            return { 'zip': {
                'zipcode': self.zipcode,
                'lat': data[address]['latitude'],
                'lng': data[address]['longitude'],
            }}
        else:
            return {'error': 'Error while getting geocoding information for ' + self.zipcode}
