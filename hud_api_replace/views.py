import csv
import json
from math import acos, cos, radians, sin
import re

from django.db import connection
from django.http import HttpResponse

from hud_api_replace.forms import HudForm
from hud_api_replace.geocode import geocode_get_data
from hud_api_replace.models import CounselingAgency, Service, Language


def geocode_zip(zipcode):
    """ Get zipcode geocoding information """

    #try:
    return geocode_get_data(zipcode, zip_only=True)
    #except:
    #    return {'error': 'Error while getting geocoding information for ' + zipcode}


def return_fields(row):
    """ Limit what fields get returned, right now it returns all fields """
    fields = CounselingAgency._meta.fields
    fields_values = {}
    for field in fields:
        fields_values[field.attname] = row[fields.index(field)]

    fields_values['distance'] = round(row[-1], 1)
    return fields_values


def get_request_variables(GET):

    """ Read query string parameters """
    variables = {}
    variables['distance'] = int(GET.get('distance', '5000'))

    variables['limit'] = int(GET.get('limit', '10'))
    variables['offset'] = int(GET.get('offset', '0')) * variables['limit']
    variables['language'] = GET.get('language', '')
    variables['service'] = GET.get('service', '')

    if variables['language'] != '':
        variables['language'] = translate_params('language', variables['language'])
    if variables['service'] != '':
        variables['service'] = translate_params('service', variables['service'])

    return variables


def translate_params(param_type, values):
    """ Change langauge/service abbreviations for their corresponding names """
    items = values.split(',')
    if param_type == 'language':
        abbrs = Language.objects.all()
    elif param_type == 'service':
        abbrs = Service.objects.all()
    else:
        return items
    pairs = {}
    for pair in abbrs:
        pairs[pair.abbr] = pair.name
    for ndx, item in enumerate(items):
        items[ndx] = pairs.get(item.upper())
    return filter(bool, items)


def get_counselors_query_select_mysql():
    return """
SELECT
    *,
    (
        %s *
        acos(
            cos(radians(%s)) *
            cos(radians(agc_ADDR_LATITUDE)) *
            cos(radians(agc_ADDR_LONGITUDE) - radians(%s)) +
            sin(radians(%s)) *
            sin(radians(agc_ADDR_LATITUDE))
        )
    ) AS distance
FROM {table}
"""


def get_counselors_query_select():
    return """
SELECT * FROM (
    SELECT
        *,
        (
            %s *
            acos(
                cos(radians(%s)) *
                cos(radians(cast(\"agc_ADDR_LATITUDE\" AS float))) *
                cos(
                    radians(cast(\"agc_ADDR_LONGITUDE\" AS float)) -
                    radians(%s)
                ) +
                sin(radians(%s)) *
                sin(radians(cast(\"agc_ADDR_LATITUDE\" AS float)))
            )
        ) AS distance
    FROM {table}
) x
"""


def get_counsel_list(zipcode, GET):
    """ Return resulting data """

    rvars = get_request_variables(GET)

    # geocoding to get zipcode lat/long
    data = geocode_zip(zipcode)
    if 'zip' in data:
        latitude = data['zip']['lat']
        longitude = data['zip']['lng']

    cursor = connection.cursor()
    if 'sqlite' in connection.vendor:
        cursor.connection.create_function('acos', 1, acos)
        cursor.connection.create_function('cos', 1, cos)
        cursor.connection.create_function('radians', 1, radians)
        cursor.connection.create_function('sin', 1, sin)

    # Use algorithm from https://stackoverflow.com/q/1916953 to find the
    # closest counselors to a given location.
    eradius = 3959  # Earth radius in miles

    mysql = 'mysql' in connection.vendor
    if mysql:
        sql_select = get_counselors_query_select_mysql()
    else:
        sql_select = get_counselors_query_select()

    sql = sql_select.format(table=CounselingAgency._meta.db_table)
    qry_args = [eradius, latitude, longitude, latitude]

    wheres = []
    if mysql:
        sql += 'HAVING distance < %s'
    else:
        wheres += ['distance < %s']
    qry_args += [rvars['distance']]

    if rvars['language']:
        wheres += [
            '({})'.format(' OR '.join(
                ('languages LIKE %' + lang + '%')
                for lang in rvars['languages']
            ))
        ]

    if rvars['service']:
        wheres += [
            '({})'.format(' OR '.join(
                ('services LIKE %' + serv + '%s')
                for serv in rvars['service']

            ))
        ]

    if wheres:
        sql += 'WHERE ' + ' AND '.join(wheres)

    sql += ' ORDER BY distance LIMIT %s OFFSET %s;'
    qry_args += [rvars['limit'], rvars['offset']]

    cursor.execute(sql, qry_args)
    result = cursor.fetchall()
    data['counseling_agencies'] = [return_fields(agc) for agc in result]

    return data


def api_entry(request, zipcode, output_format='json'):
    """ Descide what format to return data in """

    hf = HudForm({'zipcode':zipcode})

    if hf.is_valid():
        zipcode = hf['zipcode'].value()
    else:
        response = HttpResponse(content_type='application/json')
        response.write('%s' % ( {"error":"Not a Valid U.S. Zip Code"}))
        return response

    if output_format == 'csv':
        return export_csv(request, zipcode)
    else:
        return return_json(request, zipcode)


def export_csv(request, zipcode):
    """ Return resulting data in csv format """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + zipcode + '.csv"'

    data = get_counsel_list(zipcode, request.GET)
    writer = csv.writer(response)
    if data['counseling_agencies'] and len(data['counseling_agencies']) > 0:
        writer.writerow(data['counseling_agencies'][0].keys())
        for item in data['counseling_agencies']:
            writer.writerow(item.values())
    else:
        writer.writerow(['No data found'])

    return response


def return_json(request, zipcode):

    """ Return resulting data in json or jsonp format """
    callback = request.GET.get('callback', '')

    if not re.match(r'^[0-9a-zA-Z\_$]*$', callback):
        callback = ''

    data = get_counsel_list(zipcode, request.GET)

    if callback == '':
        response = HttpResponse(content_type='application/json')
        response.write(json.dumps(data))
    else:

        response = HttpResponse(content_type='application/javascript')
        response.write('%s(%s)' % (callback, json.dumps(data)))
    return response
