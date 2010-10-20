#coding: utf-8
#author: Ildus K <i.kurbangaliev@gmail.com>

from django.contrib import admin
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.admin.util import lookup_field, display_for_field, label_for_field
from django.utils.encoding import smart_unicode, force_unicode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape
from django.db import models
from django.contrib.admin.views.main import ChangeList, MAX_SHOW_ALL_ALLOWED
from django.core.paginator import Paginator, InvalidPage
from django.utils import simplejson
from django.utils.translation import gettext as _

''' Модель для добавления дополнительной таблицы в форму изменения какого либо объекта, показывающий связанные
    с этим объектом данные в виде таблиц, вложенные в отдельные fieldset 
    Поддерживается добавление, удаление объектов
'''
def _boolean_icon(field_val):
    BOOLEAN_MAPPING = {True: 'yes', False: 'no', None: 'unknown'}
    return mark_safe(u'<img src="%simg/admin/icon-%s.gif" alt="%s" />' % (settings.ADMIN_MEDIA_PREFIX, BOOLEAN_MAPPING[field_val], field_val))

class InlineChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, 
                 search_fields, list_select_related, list_per_page, list_editable, model_admin, queryset = None):
        self.qs = queryset
        super(InlineChangeList, self).__init__(request, model, list_display, list_display_links, list_filter, 
                date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin)
        
    def get_query_set(self):
        if self.qs is not None: self.root_query_set = self.qs
        return super(InlineChangeList, self).get_query_set()

class InlineTableAdmin(admin.ModelAdmin):
    
    '''
        format of inline_tables
        
        ('related_field', model_that_inlined, {
            'body_fields': ('name', 'field1', 'field2'),
            'footer_fields': (_('all'), 'summ_field1', 'avg_field2'),
            'list_per_page': 10, # 0 to all
            'filter_fields': ('has_image', ),
            'no_auto_related_name': 'related_name',
            'queryset': queryset, #queryset used for list, 'related_field' in this case not used
            'add_links': [('name', 'url'), ('name', 'url')], #popup windows for add or change_action
            'position_field': 'position', #if need change position action
        }),
        ...
    '''
    inline_tables = None
    change_form_template = 'admin/inlinetable_changeform.html'
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        
        urls = super(InlineTableAdmin, self).get_urls()

        my_urls = patterns('',
            url(r'^get_table/(\d+)/(\d+)/$', self.get_table, name = 'get_inline_table'),
            url(r'^inline_delete/(\d+)/(\d+)/$', self.inline_delete, name = 'inline_delete'),
            url(r'^increase_position/(\w+)/(\d+)/(\d+)/$', self.increase_position, name = 'increase_position'),
            url(r'^decrease_position/(\w+)/(\d+)/(\d+)/$', self.decrease_position, name = 'decrease_position'),
        )
        return my_urls + urls
    
    def get_table(self, request, inline_table_pos, edited_id):
        ''' Возвращает таблицу с данными сгенерированными из inline_tables '''
        inline_table_pos = int(inline_table_pos)
        
        def get_simple_value(obj, field_name):
            try:
                f, attr, value = lookup_field(field_name, obj)
            except (AttributeError, ObjectDoesNotExist):
                result_repr = EMPTY_CHANGELIST_VALUE
            else:
                if f is None:
                    allow_tags = getattr(attr, 'allow_tags', False)
                    boolean = getattr(attr, 'boolean', False)
                    if boolean:
                        allow_tags = True
                        result_repr = _boolean_icon(value)
                    else:
                        result_repr = smart_unicode(value)
                        
                    if not allow_tags:
                        result_repr = escape(result_repr)
                    else:
                        result_repr = mark_safe(result_repr)
                else:
                    if value is None:
                        result_repr = EMPTY_CHANGELIST_VALUE
                    if isinstance(f.rel, models.ManyToOneRel):
                        result_repr = escape(getattr(obj, f.name))
                    else:
                        result_repr = display_for_field(value, f)
                        
            if force_unicode(result_repr) == '':
                result_repr = mark_safe('&nbsp;')
                
            result_repr = conditional_escape(result_repr)
            return mark_safe(result_repr)
        
        def get_field_value(obj, field_name, return_field = False):
            if type(field_name) is list:
                fname = field_name[0]
                if len(field_name) == 1:
                    return get_field_value(obj, fname, return_field)
                else:
                    obj = getattr(obj, fname)
                    del field_name[0]
                    return get_field_value(obj, field_name, return_field)
            elif type(field_name) in (basestring, str, unicode):
                if hasattr(obj, field_name):
                    if return_field:
                        return obj, field_name
                    else:
                        return get_simple_value(obj, field_name)
                else:
                    if '.' in field_name:
                        names = field_name.split('.')
                        return get_field_value(obj, names, return_field)
                    else:
                        return field_name
            else:
                return field_name
            
        def get_label_for_field(field_name, model, objects):
            from django.db.models import get_model
            
            if '.' in field_name:
                obj, field =  get_field_value(objects[0], field_name, return_field = True)
                return label_for_field(field, get_model(obj._meta.app_label, obj._meta.object_name))
            else:
                return label_for_field(field_name, model)
        
        table = {'has_data': False}
        if self.inline_tables is not None:
            try:
                inline_table = self.inline_tables[int(inline_table_pos)]
            except:
                return HttpResponse('The inline table position is wrong')
            
            if type(inline_table[2]) is not dict:
                return HttpResponse('Third paremeter in "inline_tables" must be <i> dict </i>')
            
            try:                
                model = inline_table[1]
                table['caption'] = model._meta.verbose_name_plural
                table['caption_one_item'] = model._meta.verbose_name
            except:
                return HttpResponse('Wrong parameters')
            
            table['reload_link'] = reverse('admin:get_inline_table', args = [inline_table_pos, edited_id])
            
            add_links = inline_table[2].get('add_links')
            if not add_links:
                #try:
                    info = model._meta.app_label, model._meta.module_name
                             
                    url = reverse('admin:%s_%s_add' % info)+'?%s=%s' % (inline_table[0], edited_id)
                    caption = "%s %s" % (_("Add"), model._meta.verbose_name)
                    table['add_links'] = ((caption, url), )
                #except:
                #    table['add_links'] = []
            else:
                table['add_links'] = add_links
            
            from django.contrib.contenttypes.models import ContentType
            model_contenttype = ContentType.objects.get_for_model(model)
            
            #objects = getattr(get_object_or_404(self.model, pk = edited_id), inline_table[0]).all()
            
            body_fields = inline_table[2]['body_fields']
            footer_fields = inline_table[2].get('footer_fields', None)
            filter_fields = inline_table[2].get('filter_fields', None)
            related_name = inline_table[2].get('no_auto_related_name', None)
            position_field = inline_table[2].get('position_field', None)         
            
            list_display_links = [body_fields[0]]
            list_per_page = inline_table[2].get('list_per_page', MAX_SHOW_ALL_ALLOWED)
            qs = inline_table[2].get('queryset', None)
            if not qs:
                related_field = model._meta.get_field(inline_table[0])
                if not related_name:
                    related_name = related_field.rel.related_name or model._meta.module_name+'_set'
                qs = getattr(get_object_or_404(self.model, pk = edited_id), related_name).all()
            else:
                if callable(qs):
                    qs = qs(edited_id)
            
            cl = InlineChangeList(request, model, body_fields, list_display_links, filter_fields, 
                            None, None, False, list_per_page, None, admin.site._registry[model], queryset = qs)           
            
            objects = cl.result_list
            table['has_data'] = objects.count() > 0
            if table['has_data']:
                         
                table['header'] = [get_label_for_field(field_name, model, objects) for field_name in body_fields]
                table['body'] = []
                for obj in objects:
                    row = []
                    for field_name in body_fields:
                        row.append(get_field_value(obj, field_name))
                        
                    #actions column
                    actions = []
                    delete_link = reverse('admin:inline_delete', args = [model_contenttype.id, obj.id])
                    actions.append(mark_safe('<a href="%s" onclick="return inline_delete(this)">'
                               ' <img src="/media/admin/img/admin/icon_deletelink.gif" width="10" height="10"> </a>' % (delete_link)))
                    
                    if position_field:
                        link = reverse('admin:increase_position', args = [position_field, model_contenttype.id, obj.id])
                        actions.append(mark_safe('<a href="%s" onclick="return ajax_function(this)">'
                               ' <img src="%simg/admin/arrow-down.gif" width="10" height="10"> </a>' % (link, settings.ADMIN_MEDIA_PREFIX)))
                        
                        link = reverse('admin:decrease_position', args = [position_field, model_contenttype.id, obj.id])
                        actions.append(mark_safe('<a href="%s" onclick="return ajax_function(this)">'
                               ' <img src="%simg/admin/arrow-up.gif" width="10" height="10"> </a>' % (link, settings.ADMIN_MEDIA_PREFIX)))
                    row.append(mark_safe('&nbsp;'.join(actions)))
                    table['body'].append(row)
                
                if footer_fields:
                    table['footer'] = []
                    for field_name in footer_fields:
                        table['footer'].append(get_field_value(obj, field_name))
                
        return render_to_response('admin/inline_table.html', {'table': table, 'cl': cl})
        
    def inline_delete(self, request, content_type_id, object_id):
        ''' ajax удаление объекта '''
        from django.contrib.contenttypes.models import ContentType
        
        try:
            model = ContentType.objects.get(pk = content_type_id).model_class()
            obj = model.objects.get(pk = object_id)
        except:
            return HttpResponse('fail')
        obj.delete()
        return HttpResponse('ok')
    
    def increase_position(self, request, pos_field, content_type_id, object_id):
        ''' ajax увеличение позиции '''
        from django.contrib.contenttypes.models import ContentType
        
        try:
            model = ContentType.objects.get(pk = content_type_id).model_class()
            obj = model.objects.get(pk = object_id)
            pos = getattr(obj, pos_field)
            setattr(obj, pos_field, pos+1)            
            obj.save()
        except:
            return HttpResponse('fail')
        return HttpResponse('ok')
    
    def decrease_position(self, request, pos_field, content_type_id, object_id):
        ''' ajax уменьшение позиции '''
        from django.contrib.contenttypes.models import ContentType
        
        try:
            model = ContentType.objects.get(pk = content_type_id).model_class()
            obj = model.objects.get(pk = object_id)
            pos = getattr(obj, pos_field)
            setattr(obj, pos_field, pos-1)            
            obj.save()
        except:
            return HttpResponse('fail')
        return HttpResponse('ok')
    
class TreeChangeList(ChangeList):
    def get_results(self, request):
        paginator = Paginator(self.model.get_root_nodes(), self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        if not self.query_set.query.where:
            full_result_count = result_count
        else:
            full_result_count = self.root_query_set.count()

        can_show_all = result_count <= MAX_SHOW_ALL_ALLOWED
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.query_set._clone()
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except InvalidPage:
                result_list = ()

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator
    
class TreeEditorAdmin(admin.ModelAdmin):
    ''' Класс реализующий редактирование в дереве для объекта, работает совместно с django-treebeard '''
    ''' @todo: доделать! '''
    
    change_list_template = 'admin/treeeditor.html'
    
    try:
        from treebeard.forms import MoveNodeForm
        form = MoveNodeForm
    except:
        pass
    
    list_per_page = 2
    
    def __init__(self, *args, **kwargs):
        super(TreeEditorAdmin, self).__init__(*args, **kwargs)
        if not hasattr(self.model, 'get_root_nodes'):
            raise AssertionError('Model for TreeEditor must be Treebeard Tree')
            
    def get_changelist(self, request, **kwargs):
        return TreeChangeList
        
    def get_urls(self):
        from django.conf.urls.defaults import patterns
        
        urls = super(TreeEditorAdmin, self).get_urls()

        my_urls = patterns('',
            (r'^get_tree/$', self.get_tree),
            (r'^move_node/$', self.move_node),
            #(r'^rename/$', self.rename),
            #(r'^remove/$', self.remove),
            #(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            #     {'document_root': os.path.join(os.path.dirname(__file__),'media'), 'show_indexes': True}),
        )
        return my_urls + urls
    
    @staticmethod
    def jstree_element(obj):
        data = {
            "attr" : { "id" : str(obj.id) },
            "data": {
                "title": u"<input type='checkbox'> %s"%obj,
                "attr": {"href": '%s/'%obj.id}
            }
        }
        
        if not obj.is_leaf():
            data['children'] = []
            data['state'] = 'closed'
            
        return data
        
    def make_jstree_data(self, queryset):
        result = []
        if len(queryset) == 0:
            result.append({"data" : u"Данных нет"})
        else:
            for obj in queryset:
                data = TreeEditorAdmin.jstree_element(obj)              
                result.append(data)
        return result
    
    def get_tree(self, request):
        #self.model.fix_tree()
        ''' Возвращает дерево '''
        id = int(request.GET.get('id', 0))
        if not id:
            #nodes = self.
            nodes = self.model.get_root_nodes()
        else:
            nodes = get_object_or_404(self.model, pk = id).get_children()
            
        json_data = simplejson.dumps(self.make_jstree_data(nodes))
        return HttpResponse(json_data, mimetype = 'application/json')            
        
    def move_node(self, request):
        ''' Перемещает лист '''
        
    #def changelist_view(self, request, extra_context=None):
    #    return ''
        
    class Media:
        location_libs = settings.MEDIA_URL+'lib/js/'
        
        js = (
            location_libs+'jquery.js',
            location_libs+'jstree/jquery.jstree.js',
        )
