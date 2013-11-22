from django.http import HttpResponse
from django.template import RequestContext, loader
from django.db import connection, transaction

from hud_api_replace.geocode import GeoCode

import csv
import json

from .models import CounselingAgency

def geocode_zip( zipcode ):
    # use google api or dstk
    try:
        geocode = GeoCode( zipcode )
        return geocode.google_maps_api()
    except:
        return {'error': 'Error while getting geocoding information for ' + zipcode}
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
