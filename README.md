This represents a django project to replace HUD API.

## cron_job

This is a script that's supposed to be run nightly to load HUD data into our local table by accessing
`/cron-job/load-hud-data` on the server.

## hud_api_replace

This is the API portion, accessed from `hud-api-replace/:zipcode[.format]`. 

format can be either a `json` (default) or `csv`.

Additionally, `distance`, `limit` and `offset` query string patameters are allowed.


