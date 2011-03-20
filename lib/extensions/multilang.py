#coding: utf-8

#добавляем мультиязычность к объектам
#в модели должно быть свойство language, в котором содержится код языка (ru, en), choices = settings.LANGUAGES
# также должно быть слуг поле, чтобы собирать объекты, различающиеся языком в одну группу (свойство slug_field)
#в settings должны быть определены LANGUAGE_CODE, LANGUAGES
#если методы перекрываются, побольше наследований :)

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

class MultilangChangeList(ChangeList):
    ''' show objects of main language only (define it in settings)  '''
    
    def __init__(self, request, model, *args, **kwargs):
        self.qs = model.objects.filter(language = settings.LANGUAGE_CODE[:2])
        super(MultilangChangeList, self).__init__(request, model, *args, **kwargs)
        
    def get_query_set(self):
        if self.qs is not None: self.root_query_set = self.qs
        return super(MultilangChangeList, self).get_query_set()
    
class MultilangAdmin(admin.ModelAdmin):
    slug_field = 'alias'
    defaults = None #tuple, sample: ('name', 'title', )
    use_multilang_change_form = False
    
    def __init__(self, *args, **kwargs):
        super(MultilangAdmin, self).__init__(*args, **kwargs)
        if self.use_multilang_change_form:
            self.change_form_template = 'lib/multilang/default_change_form.html'
    
    def languages(self, obj):
        kwargs = {self.slug_field: getattr(obj, self.slug_field)}
        langs = [obj.get_language_display() for obj in self.model.objects.filter(**kwargs)]
        return ','.join(langs)
    languages.short_description = _("Languages")
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        
        urls = super(MultilangAdmin, self).get_urls()

        my_urls = patterns('', 
            url(r'^multilang_get_object/(\d+)/(\w+)/$', self.get_object_by_language, name = 'multilang_get_object'),
        )
        return my_urls + urls
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['languages'] = settings.LANGUAGES
        context['multilang_show'] = True
        context['multilang_slug_field'] = self.slug_field
        context['multilang_main_language'] = settings.LANGUAGE_CODE[:2]
        return super(MultilangAdmin, self).render_change_form(request, context, add, change, form_url, obj)
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return MultilangChangeList
    
    def get_object_by_language(self, request, object_id, lang):
        obj = get_object_or_404(self.model, pk = object_id)
        
        defaults = {}
        if self.defaults:
            for prop in self.defaults:
                defaults[prop] = getattr(obj, prop)
        
        kwargs = {
            self.slug_field: getattr(obj, self.slug_field),
            'language': lang,
            'defaults': defaults,
        }    
        new, created = self.model.objects.get_or_create(**kwargs)        
        info = new._meta.app_label, new._meta.module_name            
        link = reverse('admin:%s_%s_change' % info, args = [new.id])
        return redirect(link)