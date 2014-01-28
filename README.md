This is a django project that provides a very basic API on top of [HUD Housing Counseling](http://portal.hud.gov/hudportal/HUD?src=/program_offices/housing/sfh/hcc)
 data.

### Environmental variable GOOGLE_MAPS_API_PRIVATE_KEY must be set.

### Environmental variable GOOGLE_MAPS_API_CLIENT_ID must be set.

### Environmental variable DJANGO_HUD_NOTIFY_EMAILS must be set.

## hud_api_replace

This module creates a basic API that returns a list of HUD-approved agencies near a given zipcode sorted by
distance in ascending order. Data returned can be in `json` or `csv` format. The API accepts `distance`, `limit`,
`offset`, `language` and `service` parameters.

# Default values:

For format is `json`, for `distance` is 5000, for `limit` is 10, and for `offset` is 0. `language` and `service`
have no default values.

The API can be accessed from `hud-api-replace/:zipcode` address.

# Examples:

Return 10 closest to 20005 agencies, formatted as `json`:

`hud-api-replace/20005`

Return 5 closest to the given zipcode agencies, formatted as `json`:

`hud-api-replace/20005.json?limit=5` or `hud-api-replace/20005?limit=5`

Return at most 10 agencies that are closer than 5 miles to 20005, formatted as `csv`:

`hud-api-replace/20005.csv?distance=5`

Return page 2 of the agencies that are located not further than 100 miles from 20005, 5 agencies per page,
formatted as `json`:

`hud-api-replace/20005?limit=5&offset=1&distance=100`

Get the list of agencies that speak English *OR* Korean:

`hud-api-replace/20005?language=eng,kor`

Get list of agencies that provide [Mortgage Delinquency and Default Resolution Counse] and [Financial, Budgeting
and Credit Repair Workshops] services:

`20005/?service=dfc,fbw`

## Service Abbreviations:

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

## Language Abbreviations:

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

## Installation

Add `hud_api_replace` to `INSTALLED_APPS` in settings file. If `South` is used, migrations folder will have to be
removed. Make sure variables `settings.GOOGLE_MAPS_API_PRIVATE_KEY`, `settings.GOOGLE_MAPS_API_CLIENT_ID` and
`settings.DJANGO_HUD_NOTIFY_EMAILS` are set.

`manage.py syncdb`

will create three tables used by the module.

`manage.py cron_job`

will load HUD data into local database.

include hud_api_replace.urls.

## cron_job management command

`manage.py cron_job` will load HUD data into local database. Error messages will be emailed to a list of emails
defined in `$DJANGO_HUD_NOTIFY_EMAILS`
