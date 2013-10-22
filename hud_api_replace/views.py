# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db import connection, transaction

import csv
import json
import urllib2
import math
# need to pip install dstk first
import dstk

import logging

from .models import CounselingAgency


logging.basicConfig(level=logging.DEBUG, filename='/tmp/aaaa')


def google_maps_api( zipcode ):
    # Google API
    address = zipcode
    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&" % address
    try:
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
    except:
        # how to handle errors?
        logging.exception(' OOPS: ')
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
        logging.exception(' OOPS: ')
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

    fields_values['distance'] = math.floor( row[ -1 ] )

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
#    response = HttpResponse(content_type='application/json')
#    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.json"'
    response = HttpResponse()
    data = get_counsel_list( zipcode, request.GET )
    response.write( json.dumps( data ) )
    return response
