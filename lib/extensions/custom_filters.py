#coding: utf-8

from django.contrib import admin

from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.filterspecs import FilterSpec
from django.db import models

class FakeField(models.Field):
    def __init__(self, **kwargs):
        self.rel_fields = kwargs.pop('rel_fields') if kwargs.has_key('rel_fields') else None
        super(FakeField, self).__init__(**kwargs)

class CustomFilteredChangeList(ChangeList):
    def get_filters(self, request):
        filter_specs = []
        if self.list_filter:
            filter_fields = []
            for field_name in self.list_filter:
                if '__' in field_name:
                    names = field_name.split('__')
                    field = FakeField(name = names[0], rel_fields = names)
                else:
                    field = self.lookup_opts.get_field(field_name)
                filter_fields.append(field)
                
            for f in filter_fields:
                spec = FilterSpec.create(f, request, self.params, self.model, self.model_admin)
                if spec and spec.has_output():
                    filter_specs.append(spec)
        return filter_specs, bool(filter_specs)
    
class ExtFiltersAdmin(admin.ModelAdmin):
    def get_changelist(self, request, **kwargs):
        return CustomFilteredChangeList