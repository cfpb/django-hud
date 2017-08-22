# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hud_api_replace', '0001_initial'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='cachedgeodata',
            index_together=set([('key', 'expires')]),
        ),
    ]
