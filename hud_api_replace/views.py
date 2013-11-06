from django.conf import settings
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db import connection, transaction

import csv
import json
import urllib2
import urllib, urlparse
import hmac, base64, hashlib
# need to pip install dstk first
#import dstk

from .models import CounselingAgency

def signed_url( url, privateKey ):
    """ Google Maps API requires signature parameter, this function generates it and returns the new url
    see example on https://developers.google.com/maps/documentation/business/webservices/auth """
    parsed = urlparse.urlparse( url )
    urlToSign = parsed.path + "?" + parsed.query
    decodedKey = base64.urlsafe_b64decode( privateKey )
    signature = hmac.new( decodedKey, urlToSign, hashlib.sha1 )
    encodedSignature = base64.urlsafe_b64encode( signature.digest() )
    return url + '&signature=' + encodedSignature

def google_maps_api( zipcode ):
    """ Google API """
    address = zipcode
    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % address
    try:
        privateKey = settings.GOOGLE_MAPS_API_PRIVATE_KEY
        clientID = settings.GOOGLE_MAPS_API_CLIENT_ID
        url += '&client=' + clientID
        url = signed_url( url, privateKey )
        response = urllib2.urlopen( url )
        jsongeocode = json.loads( response.read() )
        if jsongeocode['results'][0]['geometry']:
            lat = jsongeocode['results'][0]['geometry']['location']['lat']
            lng = jsongeocode['results'][0]['geometry']['location']['lng']
            return { 'zip': {
                'zipcode': zipcode,
                'lat': lat,
                'lng': lng,
            }}
    except KeyError:
        return {'error': 'Environmental variables GOOGLE_MAPS_API_PRIVATE_KEY and GOOGLE_MAPS_API_CLIENT_ID must be set'}
    except:
        return {'error': 'Error while getting geocoding information for ' + zipcode}


def dstk_api( zipcode ):
    # dstk = dstk.DSTK( {'apiBase': 'http://dstk.address.com'} )
    # or set DSTK_API_BASE env variable
    # by default connects to http://datasciencetoolkit.org
    dst = dstk.DSTK()
    address = zipcode + ', US'
    data = dst.street2coordinates( [address] )
    if isinstance( data[address], dict ):
        return { 'zip': {
            'zipcode': zipcode,
            'lat': data[address]['latitude'],
            'lng': data[address]['longitude'],
        }}
    else:
        return {'error': 'Error while getting geocoding information for ' + zipcode}


def geocode_zip( zipcode ):
    # use google api or dstk
    return google_maps_api( zipcode )
    #return dstk_api( zipcode )


# list of fields that are returned from the API
# right now returns all fields
def return_fields( row ):
    fields = CounselingAgency._meta.fields
    #fields_values = { field.attname: getattr( row, field.attname ) for field in fields }
    fields_values = {}
    for field in fields:
        fields_values[ field.attname ] = row[ fields.index( field ) ]

    fields_values['distance'] = round( row[ -1 ], 1 )

    return fields_values


def get_counsel_list( zipcode, GET ):
    distance = int(GET.get( 'distance', '5000' ))
    limit = int(GET.get( 'limit', '10' ))
    offset = int(GET.get( 'offset', '0' )) * limit

    # geocoding to get zipcode lat/long
    data = geocode_zip( zipcode )
    if 'zip' in data:
        latitude = data['zip']['lat']
        longitude = data['zip']['lng']

        # from
        # http://stackoverflow.com/questions/1916953/filter-zipcodes-by-proximity-in-django-with-the-spherical-law-of-cosines
        eradius = 3959 # Earth radius in miles
        cursor = connection.cursor()
        sql = """SELECT *, (%f * acos( cos( radians(%f) ) * cos( radians( agc_ADDR_LATITUDE ) ) *
            cos( radians( agc_ADDR_LONGITUDE ) - radians(%f) ) + sin( radians(%f) ) * sin( radians( agc_ADDR_LATITUDE ) ) ) )
            AS distance FROM hud_api_replace_counselingagency HAVING distance < %d
            ORDER BY distance LIMIT %d OFFSET %d;""" % (eradius, latitude, longitude, latitude, distance, limit, offset)
        cursor.execute(sql)
        result = cursor.fetchall()
        data['counseling_agencies'] = [ return_fields( agc ) for agc in result ]

    return data


def api_entry( request, zipcode = 0, output_format = 'json' ):
    if output_format == 'csv':
        return export_csv( request, zipcode )
    else:
        return return_json( request, zipcode )


def export_csv( request, zipcode ):
    response = HttpResponse( content_type = 'text/csv' )
    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.csv"'

    data = get_counsel_list( zipcode, request.GET )
    writer = csv.writer( response )
    writer.writerow( data )

    return response


def return_json( request, zipcode ):
    response = HttpResponse(content_type='application/json')
#    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.json"'
    response = HttpResponse()
    data = get_counsel_list( zipcode, request.GET )
    response.write( json.dumps( data ) )
    return response
