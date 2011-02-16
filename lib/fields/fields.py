#coding: utf-8

from django.db import models
from django import forms
from django.forms import ValidationError
from south.modelsinspector import add_introspection_rules
import widgets
from popup.foreign_key import ForeignKeyField
from popup.mm_field import PopupManyToManyField
from django.contrib.contenttypes.models import ContentType
from django.core import validators
from django.utils.translation import ugettext_lazy as _

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

class NiceFileField(forms.Field):
    widget = widgets.NiceFileWidget
    default_error_messages = {
        'invalid': _(u"No file was submitted. Check the encoding type on the form."),
        'missing': _(u"No file was submitted."),
        'empty': _(u"The submitted file is empty."),
        'max_length': _(u'Ensure this filename has at most %(max)d characters (it has %(length)d).'),
        'contradiction': _(u'Please either submit a file or clear the clear checkbox, not both.')
    }

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        super(NiceFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        if data in validators.EMPTY_VALUES:
            return None

        # UploadedFile objects should have name and size attributes.
        try:
            file_name = data.name
            file_size = data.size
        except AttributeError:
            raise ValidationError(self.error_messages['invalid'])

        if self.max_length is not None and len(file_name) > self.max_length:
            error_values =  {'max': self.max_length, 'length': len(file_name)}
            raise ValidationError(self.error_messages['max_length'] % error_values)
        if not file_name:
            raise ValidationError(self.error_messages['invalid'])
        if not file_size:
            raise ValidationError(self.error_messages['empty'])

        return data

    def clean(self, data, initial=None):
        # If the widget got contradictory inputs, we raise a validation error
        if data is widgets.FILE_INPUT_CONTRADICTION:
            raise ValidationError(self.error_messages['contradiction'])
        # False means the field value should be cleared; further validation is
        # not needed.
        if data is False:
            if not self.required:
                return False
            # If the field is required, clearing is not possible (the widget
            # shouldn't return False data in that case anyway). False is not
            # in validators.EMPTY_VALUES; if a False value makes it this far
            # it should be validated from here on out as None (so it will be
            # caught by the required check).
            data = None
        if not data and initial:
            return initial
        return super(NiceFileField, self).clean(data)

    def bound_data(self, data, initial):
        if data in (None, widgets.FILE_INPUT_CONTRADICTION):
            return initial
        return data

class RemovableFileField(models.FileField):
    def get_internal_type(self):
        return 'FileField'

    def save_form_data(self, instance, data):
        if data is not None:
            if not data:
                data = ''
            setattr(instance, self.name, data)

    def formfield(self, **kwargs):
        defaults = {'form_class': NiceFileField, 'max_length': self.max_length}
        # If a file has been provided previously, then the form doesn't require
        # that a new file is provided this time.
        # The code to mark the form field as not required is used by
        # form_for_instance, but can probably be removed once form_for_instance
        # is gone. ModelForm uses a different method to check for an existing file.
        if 'initial' in kwargs:
            defaults['required'] = False
        defaults.update(kwargs)
        return super(RemovableFileField, self).formfield(**defaults)
    
add_introspection_rules([
    (
        [RemovableFileField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.fields\.RemovableFileField"])
