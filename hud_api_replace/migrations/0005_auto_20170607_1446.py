# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hud_api_replace', '0004_auto_20170605_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='counselingagency',
            name='geocode_source',
        ),
        migrations.RemoveField(
            model_name='counselingagency',
            name='last_geocode_failed',
        ),
        migrations.RemoveField(
            model_name='counselingagency',
            name='last_geocoded_at',
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='correction_needed',
            field=models.DateTimeField(null=True),
        ),
    ]
