# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hud_api_replace', '0003_auto_20170605_1338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='counselingagency',
            old_name='county_nme',
            new_name='county_NME',
        ),
        migrations.AlterField(
            model_name='counselingagency',
            name='agc_ADDR_LATITUDE',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='counselingagency',
            name='agc_ADDR_LONGITUDE',
            field=models.FloatField(null=True),
        ),
    ]
