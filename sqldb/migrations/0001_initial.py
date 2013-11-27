# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tn'
        db.create_table('SUBSCRIPTIONVERSION', (
            ('TN', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('LRN', self.gf('django.db.models.fields.IntegerField')()),
            ('SVType', self.gf('django.db.models.fields.IntegerField')()),
            ('SPID', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('LNPType', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('ActivationTS', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'sqldb', ['Tn'])

        # Adding model 'LastTxn'
        db.create_table(u'sqldb_lasttxn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('LAST_TXN_ID', self.gf('django.db.models.fields.IntegerField')()),
            ('TXN_TIMESTAMP', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'sqldb', ['LastTxn'])


    def backwards(self, orm):
        # Deleting model 'Tn'
        db.delete_table('SUBSCRIPTIONVERSION')

        # Deleting model 'LastTxn'
        db.delete_table(u'sqldb_lasttxn')


    models = {
        u'sqldb.lasttxn': {
            'LAST_TXN_ID': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'LastTxn'},
            'TXN_TIMESTAMP': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'sqldb.tn': {
            'ActivationTS': ('django.db.models.fields.DateTimeField', [], {}),
            'LNPType': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'LRN': ('django.db.models.fields.IntegerField', [], {}),
            'Meta': {'object_name': 'Tn', 'db_table': "'SUBSCRIPTIONVERSION'"},
            'SPID': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'SVType': ('django.db.models.fields.IntegerField', [], {}),
            'TN': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['sqldb']