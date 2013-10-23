This represents a django project to replace HUD API.

## hud_api_replace

This module is used to return a list of HUD-approved agencies sorted ascending by distance from a given zipcode. It
returns data in `json` or `csv` format. Additionally, `distance`, `limit` and `offset` patameters are allowed.

Default value for format is `json`, for `distance` is 5000, for `limit` is 10, and for `offset` is 0.

The API can be accessed from `hud-api-replace/:zipcode` address.

Examples:

Return 10 closest to 20005 agencies, formatted as `json`:

`hud-api-replace/20005`

Return 5 closest to the given zipcode agencies, formatted as `json`:

`hud-api-replace/20005.json?limit=5` or `hud-api-replace/20005?limit=5`

Return at most 10 agencies that are closer than 5 miles to 20005, formatted as `csv`:

`hud-api-replace/20005.csv?distance=5`

Return page 2 of the agencies that are located not further than 100 miles from 20005, 5 agencies per page,
formatted as `json`:

`hud-api-replace/20005?limit=5&offset=1&distance=100`

## cron_job management command

`./manage.py cron_job` will load HUD data into hud_api_replace_counselingagencies local table. Error messages will
be printed to stderr if any, but no other means of error notification are present.
