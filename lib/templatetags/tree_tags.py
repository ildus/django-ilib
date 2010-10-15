# -*- coding:utf-8 -*-

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings
from lib.tree import TreeEditorAdmin
from django.utils import simplejson
from django.contrib.admin.util import lookup_field, display_for_field, label_for_field
from django.utils.encoding import smart_str, force_unicode

register=template.Library()

@register.simple_tag
def jstree_element(obj):
    if obj:
        json_data = simplejson.dumps(TreeEditorAdmin.jstree_element(obj))
        return json_data
    return ''
    
def result_headers(cl):
    result = ['id']
    for field_name in cl.list_display:
        label = label_for_field(field_name, cl.model, model_admin = cl.model_admin)
        result.append(unicode(label))
        
    return result
    
def result_models(cl):
    def model_format(name, width = 200, hidden = False, key = False, index = None):
        return {'name': name, 'index': index or name, 'width': width, 'hidden': hidden, 'key': key}
    
    results = [model_format('id', 1, True, True)]
    for i, field_name in enumerate(cl.list_display):
        results.append(model_format(field_name))
        
    return results

@register.inclusion_tag('admin/includes/tree_results.html')
def tree_resultlist(cl):
    return {
        'result_headers': mark_safe(simplejson.dumps(result_headers(cl))),
        'result_models': mark_safe(simplejson.dumps(result_models(cl))),
        'expand_column': cl.model_admin.expand_column,
    }
