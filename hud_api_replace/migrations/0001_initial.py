# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CounselingAgency'
        db.create_table(u'hud_api_replace_counselingagency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('agcid', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('adr1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('adr2', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('nme', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('statecd', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('weburl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('zipcd', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('agc_ADDR_LATITUDE', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('agc_ADDR_LONGITUDE', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('languages', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('services', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parentid', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('county_nme', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('mailingadr1', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mailingadr2', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mailingcity', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('mailingzipcd', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('mailingstatecd', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('state_NME', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state_FIPS_CODE', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('faithbased', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('colonias_IND', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('migrantwkrs_IND', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('agc_STATUS', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('agc_SRC_CD', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('counslg_METHOD', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'hud_api_replace', ['CounselingAgency'])


    def backwards(self, orm):
        # Deleting model 'CounselingAgency'
        db.delete_table(u'hud_api_replace_counselingagency')


    models = {
        u'hud_api_replace.counselingagency': {
            'Meta': {'object_name': 'CounselingAgency'},
            'adr1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'adr2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'agc_ADDR_LATITUDE': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'agc_ADDR_LONGITUDE': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'agc_SRC_CD': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'agc_STATUS': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'agcid': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'colonias_IND': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'counslg_METHOD': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'county_nme': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'faithbased': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mailingadr1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mailingadr2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mailingcity': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mailingstatecd': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'mailingzipcd': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'migrantwkrs_IND': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'nme': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parentid': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'services': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state_FIPS_CODE': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state_NME': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'statecd': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'weburl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zipcd': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['hud_api_replace']
