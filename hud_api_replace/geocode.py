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
            if jsongeocode['results'][0]['geometry']:
                lat = jsongeocode['results'][0]['geometry']['location']['lat']
                lng = jsongeocode['results'][0]['geometry']['location']['lng']
                return { 'zip': {
                    'zipcode': self.zipcode,
                    'lat': lat,
                    'lng': lng,
                }}
        except KeyError:
            return {'error': 'Environmental variables GOOGLE_MAPS_API_PRIVATE_KEY and GOOGLE_MAPS_API_CLIENT_ID must be set'}
        except:
            return {'error': 'Error while getting geocoding information for ' + self.zipcode}


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
