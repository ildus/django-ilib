#coding: utf-8

from django.db import models
from south.modelsinspector import add_introspection_rules
import widgets
from popup.foreign_key import ForeignKeyField
from popup.mm_field import PopupManyToManyField
from django.contrib.contenttypes.models import ContentType

class MarkdownTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs['widget'] = widgets.MarkdownEditor
        return super(MarkdownTextField, self).formfield(**kwargs)
        
add_introspection_rules([
    (
        [MarkdownTextField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.fields\.MarkdownTextField"])
        
class RichTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs['widget'] = widgets.TinyMCEEditor
        return super(RichTextField, self).formfield(**kwargs)

add_introspection_rules([
    (
        [RichTextField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.fields\.RichTextField"])

class ForeignKeyRelated(models.ForeignKey):
    collection = None
    related_field = None
    
    def __init__(self, to, to_field=None, rel_class=models.ManyToOneRel, **kwargs):
        if 'collection' in kwargs:
            self.collection = kwargs.pop('collection')
        if 'related_field' in kwargs:
            self.related_field = kwargs.pop('related_field')
        super(ForeignKeyRelated, self).__init__(to, to_field, rel_class, **kwargs)
    
    def formfield(self, **kwargs):
        content_type = ContentType.objects.get_for_model(self.rel.to)
                
        if self.collection:
            kwargs['widget'] = widgets.ForeignKeyRelatedWidget(content_type=content_type, collection = self.collection,
                                                               related_field = self.related_field)
        
        return super(ForeignKeyRelated, self).formfield(**kwargs)
    
add_introspection_rules([
    (
        [ForeignKeyRelated], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.fields\.ForeignKeyRelated"])
