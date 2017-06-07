# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('hud_api_replace', '0002_remove_cachedgeodata_expires'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZipCode',
            fields=[
                ('zip', models.CharField(max_length=5, serialize=False, primary_key=True)),
                ('lat', models.FloatField(null=True, verbose_name=b'Latitude')),
                ('lon', models.FloatField(null=True, verbose_name=b'Longitude')),
            ],
        ),
        migrations.DeleteModel(
            name='CachedGeodata',
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='geocode_address_override',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='geocode_source',
            field=models.CharField(default=b'hud', max_length=20),
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='last_geocode_failed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='last_geocoded_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='source_data_hash',
            field=models.CharField(max_length=65, blank=True),
        ),
        migrations.AddField(
            model_name='counselingagency',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 5, 17, 38, 29, 450981, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
