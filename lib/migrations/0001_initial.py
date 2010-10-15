# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SimpleImage'
        db.create_table('lib_simpleimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('lib', ['SimpleImage'])


    def backwards(self, orm):
        
        # Deleting model 'SimpleImage'
        db.delete_table('lib_simpleimage')


    models = {
        'lib.simpleimage': {
            'Meta': {'object_name': 'SimpleImage'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['lib']
