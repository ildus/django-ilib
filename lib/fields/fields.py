#coding: utf-8

from django.db import models
from south.modelsinspector import add_introspection_rules
import widgets
from popup.foreign_key import ForeignKeyField
from popup.mm_field import PopupManyToManyField

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
