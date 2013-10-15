# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db import connection, transaction

import csv
import json
import urllib2
import logging

from .models import CounselingAgency


def geocode_zip( zipcode ):
    # use google api or dstk

    # Google API
    address = zipcode
    address = 'ABCDE'
    url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&" % address
    logging.basicConfig(level=logging.DEBUG, filename='/tmp/aaaa')
    try:
        response = urllib2.urlopen( url )
        jsongeocode = json.loads( response.read() )
        if jsongeocode['results'][0]['geometry']:
            lat = jsongeocode['results'][0]['geometry']['location']['lat']
            lng = jsongeocode['results'][0]['geometry']['location']['lng']
            return [lat, lng]
    except:
        # how to handle errors?
        logging.exception(' OOPS: ')
        return []

    # for now returns default lat long for 22030
    return [38.8462, -77.3279]


def get_counsel_list( zipcode, GET ):
    distance = GET.get( 'distance', 5000 )
    limit = GET.get( 'limit', 10 )
    offset = GET.get( 'offset', 0 ) * limit

    # geocoding to get zipcode lat/long
    (latitude, longitude) = geocode_zip( zipcode )

    # from
    # http://stackoverflow.com/questions/1916953/filter-zipcodes-by-proximity-in-django-with-the-spherical-law-of-cosines
    eradius = 3959 # Earth radius in miles
    cursor = connection.cursor()
    sql = """SELECT id, (%f * acos( cos( radians(%f) ) * cos( radians( agc_ADDR_LATITUDE ) ) *
        cos( radians( agc_ADDR_LONGITUDE ) - radians(%f) ) + sin( radians(%f) ) * sin( radians( agc_ADDR_LATITUDE ) ) ) )
        AS distance FROM hud_api_replace_counselingagency HAVING distance < %d
        ORDER BY distance LIMIT %d OFFSET %d;""" % (eradius, latitude, longitude, latitude, distance, limit, offset)
    cursor.execute(sql)
    ids = [row[0] for row in cursor.fetchall()]

    return CounselingAgency.objects.filter( id__in = ids )


def api_entry( request, zipcode = 0, output_format = 'json' ):
    if output_format == 'csv':
        return export_csv( request, zipcode )
    else:
        return export_json( request, zipcode )

# list of fields that are returned from the API
def return_fields( row ):
    return [ row.nme, row.adr1, row.adr2, row.zipcd ]


def export_csv( request, zipcode ):
    response = HttpResponse( content_type = 'text/csv' )
    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.csv"'

    data = get_counsel_list( zipcode, request.GET )
    writer = csv.writer( response )
    for row in data:
        writer.writerow( return_fields( row ) )

    return response

def export_json( request, zipcode ):
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.json"'
    data = get_counsel_list( zipcode, request.GET )
    for row in data:
        response.write( json.dumps( return_fields( row ) ) )
    return response
