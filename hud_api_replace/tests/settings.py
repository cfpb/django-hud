from __future__ import absolute_import, unicode_literals


SECRET_KEY = 'not needed'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'hud_api_replace',
)
