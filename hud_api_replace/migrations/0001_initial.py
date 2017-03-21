# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CachedGeodata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=255)),
                ('lat', models.FloatField(null=True, verbose_name=b'Latitude')),
                ('lon', models.FloatField(null=True, verbose_name=b'Longitude')),
                ('expires', models.PositiveIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CounselingAgency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('agcid', models.CharField(max_length=9)),
                ('adr1', models.CharField(max_length=255)),
                ('adr2', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=100)),
                ('fax', models.CharField(max_length=20)),
                ('nme', models.CharField(max_length=255)),
                ('phone1', models.CharField(max_length=20)),
                ('statecd', models.CharField(max_length=2)),
                ('weburl', models.CharField(max_length=255)),
                ('zipcd', models.CharField(max_length=10)),
                ('agc_ADDR_LATITUDE', models.CharField(max_length=40)),
                ('agc_ADDR_LONGITUDE', models.CharField(max_length=40)),
                ('languages', models.CharField(max_length=255)),
                ('services', models.CharField(max_length=1500)),
                ('parentid', models.CharField(max_length=9)),
                ('county_nme', models.CharField(max_length=255)),
                ('phone2', models.CharField(max_length=20)),
                ('mailingadr1', models.CharField(max_length=255)),
                ('mailingadr2', models.CharField(max_length=255)),
                ('mailingcity', models.CharField(max_length=255)),
                ('mailingzipcd', models.CharField(max_length=10)),
                ('mailingstatecd', models.CharField(max_length=2)),
                ('state_NME', models.CharField(max_length=50)),
                ('state_FIPS_CODE', models.CharField(max_length=255)),
                ('faithbased', models.BooleanField()),
                ('colonias_IND', models.BooleanField()),
                ('migrantwkrs_IND', models.BooleanField()),
                ('agc_STATUS', models.CharField(max_length=255)),
                ('agc_SRC_CD', models.CharField(max_length=255)),
                ('counslg_METHOD', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbr', models.CharField(unique=True, max_length=5)),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbr', models.CharField(unique=True, max_length=5)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
