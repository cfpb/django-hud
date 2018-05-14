# ⚠ Deprecation Notice ⚠ 

**This project is a legacy API and is longer being actively maintained or used to serve data to consumerfinance.gov.** Please use the officially supported [HUD API](https://data.hud.gov/housing_counseling.html) in its place. For those interested, it may continue to serve as a model stand-alone API of HUD Housing Counseling data.


[![Build Status](https://travis-ci.org/cfpb/django-hud.svg?branch=master)](https://travis-ci.org/cfpb/django-hud) [![Coverage Status](https://coveralls.io/repos/github/cfpb/django-hud/badge.svg?branch=master)](https://coveralls.io/github/cfpb/django-hud?branch=master)

# django-hud

`django-hud` is a Django project that provides a very basic API on top of [HUD Housing
Counseling](http://portal.hud.gov/hudportal/HUD?src=/program_offices/housing/sfh/hcc) data. It returns a list of
HUD approved housing counseling agencies throughout the country that can provide advice on buying a home, renting,
defaults, foreclosures, and credit issues near a given zipcode sorted by distance from it in ascending order.

### Parameters:

| Parameter  | Type                    | Default value | Short Description                                                 |
|:---------- |:----------------------- |:-------------:|:----------------------------------------------------------------- |
| `distance` | integer (in miles)      | 5000          | Distance between zipcode area centroid and counseling agency      |
| `limit`    | integer                 | 10            | Number of results to return                                       |
| `offset`   | integer                 | 0             | Number of times to skip `limit` items before returning results    |
| `language` | string, comma separated | N/A           | A list of languages either of which is spoken in agency           |
| `service`  | string, comma separated | N/A           | A list of services either of which is provided by agency          |

Data returned can be in `json` (default) or `csv` format. To set the format append `.json` or `.csv` to the zipcode
value when accessing the API.

The API can be accessed from `hud-api-replace/:zipcode` address.

### Examples:

Return 10 closest to 20005 agencies, formatted as `json`:

`hud-api-replace/20005`

Return 5 closest to the given zipcode agencies, formatted as `json`:

`hud-api-replace/20005.json?limit=5` or `hud-api-replace/20005?limit=5`

Return at most 10 agencies that are closer than 5 miles to 20005, formatted as `csv`:

`hud-api-replace/20005.csv?distance=5`

Return page 2 of the agencies that are located not further than 100 miles from 20005, 5 agencies per page,
formatted as `json`:

`hud-api-replace/20005?limit=5&offset=1&distance=100`

Get the list of agencies that speak English or Korean:

`hud-api-replace/20005?language=eng,kor`

Get list of agencies that provide [Mortgage Delinquency and Default Resolution Counse] or [Financial, Budgeting
and Credit Repair Workshops] services:

`hud-api-replace/20005/?service=dfc,fbw`

### Service Abbreviations:

| abbr | name                                               |
|:---- |:-------------------------------------------------- |
| DRC  | Mobility and Relocation Counseling                 |
| FHW  | Fair Housing Pre-Purchase Education Workshops      |
| NDW  | Non-Delinquency Post Purchase Workshops            |
| PPW  | Pre-purchase Homebuyer Education Workshops         |
| MOI  | Marketing and Outreach Initiatives                 |
| HIC  | Home Improvement and Rehabilitation Counseling     |
| PLW  | Predatory Lending Education Workshops              |
| FBC  | Financial Management/Budget Counseling             |
| RHW  | Rental Housing Workshops                           |
| LM   | Loss Mitigation                                    |
| DFW  | Resolving/Preventing Mortgage Delinquency Workshop |
| RMC  | Reverse Mortgage Counseling                        |
| RHC  | Rental Housing Counseling                          |
| FBW  | Financial, Budgeting and Credit Repair Workshops   |
| PPC  | Pre-purchase Counseling                            |
| DFC  | Mortgage Delinquency and Default Resolution Counse |
| HMC  | Services for Homeless Counseling                   |

### Language Abbreviations:

| abbr | name             |
|:----:|:---------------- |
| ITA  | Italian          |
| TUR  | Turkish          |
| VIE  | Vietnamese       |
| OTH  | Other            |
| CHI  | Chinese Mandarin |
| GER  | German           |
| FRE  | French           |
| ASL  | ASL              |
| HIN  | Hindi            |
| SPA  | Spanish          |
| HMO  | Hmong            |
| POL  | Polish           |
| POR  | Portuguese       |
| ENG  | English          |
| FAR  | Farsi            |
| KOR  | Korean           |
| CRE  | Creole           |
| CAM  | Cambodian        |
| CAN  | Cantonese        |
| UKR  | Ukrainian        |
| SWA  | Swahili          |
| ARA  | Arabic           |
| IND  | Indonesian       |
| RUS  | Russian          |
| CZE  | Czech            |

## JSON-P

Add `callback` parameter to the call. Works only when format is `json`.


## Testing

* To run unit tests against a testing matrix of Python and Django versions, run:

```sh
$ tox
```

You can also run a particular version, e.g.:

```sh
$ tox -e py27-dj18
```

## Installation

* Add `hud_api_replace` to `INSTALLED_APPS` in settings file.

* Make sure you've set an environment variable `MAPBOX_ACCESS_TOKEN`, as described [here](http://geocoder.readthedocs.io/providers/Mapbox.html#environment-variables). If you need a mapbox token, [sign up here](https://www.mapbox.com/studio/signup/?path=%2Faccount)

* `manage.py syncdb` to create three tables used by the module.

* `manage.py load_hud_data` to load HUD data into local database.

* include hud_api_replace.urls.

## load_hud_data management command

`manage.py load_hud_data` will load HUD data into local database. Error messages will be emailed to a list of emails
defined in `$DJANGO_HUD_NOTIFY_EMAILS`
