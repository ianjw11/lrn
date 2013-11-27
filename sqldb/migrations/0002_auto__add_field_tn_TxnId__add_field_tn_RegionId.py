# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tn.TxnId'
        db.add_column('SUBSCRIPTIONVERSION', 'TxnId',
                      self.gf('django.db.models.fields.IntegerField')(default=195114, db_column='TXN_ID'),
                      keep_default=False)

        # Adding field 'Tn.RegionId'
        db.add_column('SUBSCRIPTIONVERSION', 'RegionId',
                      self.gf('django.db.models.fields.CharField')(default='ma', max_length=3),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Tn.TxnId'
        db.delete_column('SUBSCRIPTIONVERSION', 'TXN_ID')

        # Deleting field 'Tn.RegionId'
        db.delete_column('SUBSCRIPTIONVERSION', 'RegionId')


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
            'RegionId': ('django.db.models.fields.CharField', [], {'default': "'ma'", 'max_length': '3'}),
            'SPID': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'SVType': ('django.db.models.fields.IntegerField', [], {}),
            'TN': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'TxnId': ('django.db.models.fields.IntegerField', [], {'default': '195114', 'db_column': "'TXN_ID'"})
        }
    }

    complete_apps = ['sqldb']