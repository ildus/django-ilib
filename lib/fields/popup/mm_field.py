#coding: utf-8

#Поле для удобного выбора ManyToManyField
#Поддерживает деревья и списки
#В списках есть фильтрация по первой букве и постраничка

from django.utils import simplejson
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.conf import settings
from south.modelsinspector import add_introspection_rules
from django import forms
from django.db import models
from django.forms.util import  flatatt
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404

def is_treebeard(model):
    return hasattr(model, 'get_root_nodes')

class MMListWidget(forms.SelectMultiple):
    content_type = None
    field = None
    is_tree = False
    
    def __init__(self, *args, **kwargs):

        if kwargs.has_key("content_type"):
            self.content_type = kwargs.pop("content_type")
            
        if kwargs.has_key("field"):
            self.field = kwargs.pop("field")
            
        if kwargs.has_key("is_tree"):
            self.is_tree = kwargs.pop("is_tree")
                
        super(MMListWidget,self).__init__(*args,**kwargs)
        
    def render(self, name, value,  attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        field = self.content_type.model_class()._meta.get_field_by_name(self.field)[0]
        
        hiddens = []
        if value:
            for i, v in enumerate(value):
                attrs = {}
                
                attrs['pk'] = v
                obj = field.rel.to.objects.get(pk = v)
                attrs['text'] = unicode(obj)
                hiddens.append(attrs)
        
        context = {
            'hiddens': hiddens,
            'name': name,
            'media':settings.MEDIA_URL,
            'field_name': self.field,
            'content_type_id': self.content_type.id,
            'is_tree': self.is_tree,
        }
        return mark_safe(render_to_string('lib/many_to_many/mm_field.html', context))
    
    class Media:
        js = (
            settings.MEDIA_URL+'lib/js/foreign/dojo_init.js',
            'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dojo/dojo.xd.js',
            settings.MEDIA_URL+'lib/js/foreign/actions.js',
        )
        css = {
            'all':(
              'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dijit/themes/tundra/tundra.css',
              settings.MEDIA_URL+'lib/css/mm_field.css',
        )}

class PopupManyToManyField(models.ManyToManyField):
    '''  Поле выбора для ForeignKey
         Можно выбирать в дереве если указаны родительские поля в parent_fields
         title_field нужен для фильтрации по символам 
    '''
    parent_fields = None
    title_field = None
    
    def __init__(self, to, **kwargs):
        self.parent_fields = kwargs.pop('parents') if kwargs.has_key('parents') else None
        self.title_field = kwargs.pop('title_field') if kwargs.has_key('title_field') else None
        super(PopupManyToManyField, self).__init__(to, **kwargs)
        self.help_text = ''
    
    def formfield(self, **kwargs):
        content_type = ContentType.objects.get_for_model(self.model)
        field = self.name
        
        is_tree = self.parent_fields or is_treebeard(self.rel.to)
        kwargs['widget'] = MMListWidget(content_type=content_type, field=field, is_tree = is_tree)
        
        return super(PopupManyToManyField, self).formfield(**kwargs)
        
add_introspection_rules([
    (
        [PopupManyToManyField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.popup\.mm_field\.PopupManyToManyField"])