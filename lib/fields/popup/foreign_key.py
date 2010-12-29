#coding: utf-8

#Поле для удобного выбора других ForeignKey
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
from django.db.models.fields.related import ManyToManyRel

def is_treebeard(model):
    return hasattr(model, 'get_root_nodes')

ROOT_NODE_NAME = 'root'

def ref(item):
    return '%s_%s' % (item._meta.module_name, item.pk)

def generate_tree(parent, field, node, page = 1, id = 0):
    result = []   
    
    def get_obj(item):
        obj =  {
               '$ref': ref(item),
               'pk': item.pk,
               'name': unicode(item), 
               'type': item._meta.module_name,
               'field_name': field.name,
               'selectable': item._meta.module_name == parent._meta.module_name
        }
        
        if item._meta.module_name != parent._meta.module_name:
            obj['children'] = True
            
        return obj
    
    def add_items(model, related_name = None, pk = None):
        items = [get_object_or_404(model, pk = pk)] if pk else model.objects.all()
        for item in items:
            obj = get_obj(item)            
            if related_name and pk:
                childs = getattr(item, related_name).all()
                if childs:
                    children = []
                    for child in childs:
                        children.append(get_obj(child))
                        
                    obj['children'] = children
                else:
                    obj['children'] = False
            else:
                obj['children'] = True
                        
            result.append(obj)
    
    searched_node, searched_pk = (node, None) if node == ROOT_NODE_NAME else node.split('_') 
    if field.parent_fields:
        assert type(field.parent_fields) in (list, tuple)
        model = parent
        for one in field.parent_fields:
            is_last = field.parent_fields.index(one) == len(field.parent_fields)-1
            
            related_field = model._meta.get_field_by_name(one)[0]
            related_name = related_field.rel.related_name or model._meta.module_name+'_set'
            model = related_field.rel.to
            if searched_node == model._meta.module_name or (searched_node == ROOT_NODE_NAME and is_last):
                add_items(model, related_name, searched_pk)
                
    if searched_pk and result:
        result = result[0]
                
    return result

def fk_field_data(request, content_type_id, field_name, node = 'root'):
    model = ContentType.objects.get(pk=content_type_id).model_class()
    field = model._meta.get_field_by_name(field_name)[0]
    
    result = generate_tree(field.rel.to, field, node, page = 1)
    
    return HttpResponse(simplejson.dumps(result), mimetype = 'application/json')

def fk_select(request):
    return HttpResponse('<div id="treeOne"> </div>')

def fk_listselect(request, content_type_id, field_name, collection = 0):
    try:
        page = int(request.GET.get('page', 1))
    except:
        page = 1
        
    kwargs = {}
    model = ContentType.objects.get(pk=content_type_id).model_class()
    field = model._meta.get_field(field_name)
    if hasattr(field, 'collection'):
        if collection:
            kwargs[field.collection_field+'__pk'] = collection
    
    qs = field.rel.to.objects.filter(**kwargs)
    
    char = request.GET.get('char', None)
    if field.title_field:
        if char:
            kwargs = {
                field.title_field+'__istartswith': char,
            }
            qs = qs.filter(**kwargs)
        
    # Словари
    rus_alphabet = [mark_safe((u'<a href="?char=%(char)s">%(char)s</a>' \
                        if unichr(code)!=char else '<b style="color:black;">%(char)s</b>') % {'char':unichr(code)}) \
                                for code in range(ord(u"А"),ord(u"Я")+1)]
    en_alphabet = [mark_safe((u'<a href="?char=%(char)s">%(char)s</a>' \
                        if unichr(code)!=char else '<b style="color:black;">%(char)s</b>') % {'char':unichr(code)}) \
                            for code in range(ord(u"A"),ord(u"Z")+1)]
    digits = [mark_safe((u"<a class='char' href='?char=%(char)s'>%(char)s</a>" \
                        if unichr(code)!=char else '<b style="color:black;">%(char)s</b>') % {'char':unichr(code)}) for code in range(ord(u"0"),ord(u"9")+1)]
    
    from lib.utils import paginate
    objects, paginator, page_range = paginate(qs, page, 10)
    
    context = {
           'rus': mark_safe(u"".join(rus_alphabet)),
           'en': mark_safe(u"".join(en_alphabet)),
           'digits': mark_safe(u"".join(digits,)),
           'media':settings.MEDIA_URL,
           'objects': objects,
           'page_range': page_range,
           'field_name': field.name,
           'title_field': field.title_field,
           'for_multiple': int(isinstance(field.rel, ManyToManyRel)),
       }
    
    return render_to_response('lib/fk_select.html', context)

class ForeignKeyTreeWidget(forms.Widget):
    content_type = None
    field = None
    
    def __init__(self, *args, **kwargs):

        if kwargs.has_key("content_type"):
            self.content_type = kwargs.pop("content_type")
            
        if kwargs.has_key("field"):
            self.field = kwargs.pop("field")
            
        super(ForeignKeyTreeWidget,self).__init__(*args,**kwargs)
        
    def render(self, name, value,  attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        field = self.content_type.model_class()._meta.get_field_by_name(self.field)[0]
        
        value_name = ''
        change_url = ''
        if value:
            final_attrs['value'] = value
            obj = field.rel.to.objects.get(pk = value)
            value_name = unicode(obj)
            
            info = field.rel.to._meta.app_label, field.rel.to._meta.module_name            
            change_url = reverse('admin:%s_%s_change' % info, args = [value])
            
        hidden_field = u'<input type="hidden" %s />'  % flatatt(final_attrs)
        
        context = {
            'hidden_field': mark_safe(hidden_field),
            'name': name,
            'value': value_name,
            'media':settings.MEDIA_URL,
            'change_url': change_url,
            'content_type_id': self.content_type.id,
            'field_name': self.field,
            'dialog_title': getattr(field, 'dialog_title', None),
        }
        return mark_safe(render_to_string('lib/fk_tree.html', context))
    
    class Media:
        js = (
            settings.MEDIA_URL+'lib/js/foreign/dojo_init.js',
            'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dojo/dojo.xd.js',
            settings.MEDIA_URL+'lib/js/foreign/actions.js',
        )
        css = {
            'all':(
              'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dijit/themes/tundra/tundra.css',
              settings.MEDIA_URL+'lib/css/foreignfield.css',
        )}
        
class ForeignKeyListWidget(forms.Widget):
    content_type = None
    field = None
    
    def __init__(self, *args, **kwargs):

        if kwargs.has_key("content_type"):
            self.content_type = kwargs.pop("content_type")
            
        if kwargs.has_key("field"):
            self.field = kwargs.pop("field")
                
        super(ForeignKeyListWidget,self).__init__(*args,**kwargs)
        
    def render(self, name, value,  attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        field = self.content_type.model_class()._meta.get_field_by_name(self.field)[0]
        
        value_name = ''
        change_url = ''
        if value:
            final_attrs['value'] = value
            obj = field.rel.to.objects.get(pk = value)
            value_name = unicode(obj)
            
            info = field.rel.to._meta.app_label, field.rel.to._meta.module_name            
            change_url = reverse('admin:%s_%s_change' % info, args = [value])
            
        hidden_field = u'<input type="hidden" %s />'  % flatatt(final_attrs)
        
        context = {
            'hidden_field': mark_safe(hidden_field),
            'name': name,
            'value': value_name,
            'media':settings.MEDIA_URL,
            'change_url': change_url,
            'content_type_id': self.content_type.id,
            'field_name': self.field,
            'dialog_title': getattr(field, 'dialog_title', None),
        }
        show_simple = getattr(field, 'show_simple', False)
        if show_simple:
            return mark_safe(render_to_string('lib/fk_list_simple.html', context))
        else:
            return mark_safe(render_to_string('lib/fk_list.html', context))
    
    class Media:
        js = (
            settings.MEDIA_URL+'lib/js/foreign/dojo_init.js',
            'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dojo/dojo.xd.js',
            settings.MEDIA_URL+'lib/js/foreign/actions.js',
        )
        css = {
            'all':(
              'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dijit/themes/tundra/tundra.css',
              settings.MEDIA_URL+'lib/css/foreignfield.css',
        )}

class ForeignKeyField(models.ForeignKey):
    '''  Поле выбора для ForeignKey
         Можно выбирать в дереве если указаны родительские поля в parent_fields
         title_field нужен для фильтрации по символам 
    '''
    parent_fields = None
    title_field = None
    dialog_title = None
    show_simple = False
    
    def __init__(self, to, to_field=None, rel_class=models.ManyToOneRel, **kwargs):
        self.parent_fields = kwargs.pop('parents') if kwargs.has_key('parents') else None
        self.title_field = kwargs.pop('title_field') if kwargs.has_key('title_field') else None
        self.dialog_title = kwargs.pop('dialog_title') if kwargs.has_key('dialog_title') else None
        self.show_simple = kwargs.pop('show_simple') if kwargs.has_key('show_simple') else None
        
        super(ForeignKeyField, self).__init__(to, to_field, rel_class, **kwargs)
    
    def formfield(self, **kwargs):
        content_type = ContentType.objects.get_for_model(self.model)
        field = self.name
        
        if self.parent_fields or is_treebeard(self.rel.to):
            kwargs['widget'] = ForeignKeyTreeWidget(content_type=content_type, field=field)
        else:
            kwargs['widget'] = ForeignKeyListWidget(content_type=content_type, field=field)
        
        return super(ForeignKeyField, self).formfield(**kwargs)
        
add_introspection_rules([
    (
        [ForeignKeyField], # Class(es) these apply to
        [],         # Positional arguments (not used)
        {           # Keyword argument
        },
    ),
], ["^lib\.fields\.popup\.foreign_key\.ForeignKeyField"])


