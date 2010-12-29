#coding: utf-8

from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms import widgets
from tagging.utils import parse_tag_input
from popup.foreign_key import ForeignKeyListWidget, ForeignKeyTreeWidget
from django.core.urlresolvers import reverse

class MarkdownEditor(widgets.Textarea):
    
    def __init__(self, attrs=None):
        if not attrs: attrs = {}
        
        if not attrs.has_key('class'): attrs['class'] = ''        
        attrs['class'] += ' markdown_editor'
        
        default_attrs = {'cols': '80', 'rows': '10'}
        
        if attrs:
            default_attrs.update(attrs)
        super(MarkdownEditor, self).__init__(default_attrs)
    
    class Media:
        js = (
            settings.MEDIA_URL + 'lib/js/jquery.js',
            settings.MEDIA_URL + 'lib/markitup/jquery.markitup.pack.js',
            settings.MEDIA_URL + 'lib/markitup/sets/markdown/set.js',
        )
        
        css = {
            'screen': (
                settings.MEDIA_URL + 'lib/markitup/skins/simple/style.css',
                settings.MEDIA_URL + 'lib/markitup/sets/markdown/style.css',
            )
        }

    def render(self, name, value, attrs=None):       
        
        rendered = super(MarkdownEditor, self).render(name, value, attrs)
        return rendered + mark_safe('''
            <script type="text/javascript">
                $(document).ready(function()    {
                    $('textarea.markdown_editor').markItUp(mySettings);
                });
            </script>
        ''')
        
class TagsWidget(widgets.Widget):
    def render(self, name, value, attrs=None):
        output = ['<div class="tagbox" id="id_%s">'% (name)]
        if value:
            tags = parse_tag_input(value)
            for tag in tags:
                output.append(tag+',')
        output.append('</div>')
        return mark_safe(u'\n'.join(output))
    
    def value_from_datadict(self, data, files, name):
        tags = data.getlist(name)
        if type(tags) is list and len(tags)>0:
            return ','.join(map(lambda tag: '"%s"'%(tag), tags))
        else:
            return ''
    
    class Media:
        js = (
            settings.MEDIA_URL + 'lib/js/jquery.js',
            settings.MEDIA_URL + 'lib/js/jquery.tagbox.js',
            settings.MEDIA_URL + 'lib/js/tagbox_init.js',
        )
        
        css = {
            'all': (
                settings.MEDIA_URL + 'lib/css/tags.css',
            )
        }
        
class TinyMCEEditor(widgets.Textarea):
    def __init__(self, attrs=None):
        attrs = attrs or {}
        
        if not attrs.has_key('class'): attrs['class'] = ''        
        attrs['class'] += ' tinymce_editor'
        
        default_attrs = {'cols': '80', 'rows': '20'}
        
        if attrs:
            default_attrs.update(attrs)
        super(TinyMCEEditor, self).__init__(default_attrs)
    
    class Media:
        js = (            
            settings.MEDIA_URL + 'lib/js/jquery.js',
            settings.MEDIA_URL + 'lib/js/tiny_mce/tiny_mce.js',
            settings.MEDIA_URL + 'lib/js/tiny_mce/jquery.tinymce.js',
            settings.MEDIA_URL + 'lib/js/richeditor_init.js',
        )

class ForeignKeyRelatedWidget(widgets.Select):
    content_type = None
    collection = None
    related_field = None
    
    def __init__(self, *args, **kwargs):
        if kwargs.has_key("content_type"):
            self.content_type = kwargs.pop("content_type")
            
        if kwargs.has_key('collection'):
            self.collection = kwargs.pop('collection')
            
        if kwargs.has_key('related_field'):
            self.related_field = kwargs.pop('related_field')            
            
        super(ForeignKeyRelatedWidget,self).__init__(*args,**kwargs)
    
    def render(self, name, value, attrs=None, choices=()):
        if value:
            model = self.content_type.model_class()
            obj = model._default_manager.get(pk = value)
            kwargs = {}
            kwargs[self.related_field] = getattr(obj, self.related_field)
            selectable = model._default_manager.filter(**kwargs)
            self.choices = [(obj.pk, unicode(obj)) for obj in selectable]
        url = reverse('fk_related_values')
        plus = '''
            <script>
                dojo.addOnLoad(function () {
                    add_related_field('%s', 'id_%s', 'id_%s', %s, '%s', %s, %s);
                })
            </script>
        ''' % (url, self.collection, name, self.content_type.id, self.related_field, int(value == ''), value or 0)
        return mark_safe(super(ForeignKeyRelatedWidget, self).render(name, value, attrs, choices)+plus)
    
    class Media:
        js = (
            'http://ajax.googleapis.com/ajax/libs/dojo/1.5/dojo/dojo.xd.js',
            settings.MEDIA_URL + 'lib/js/foreign/related.js',
        )
        
class NiceFileWidget(widgets.FileInput):
    def __init__(self, attrs={}):
        super(NiceFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        default_attrs = {
            'class': 'lib_nf_custom',
        }
        default_attrs.update(attrs)
        standart = super(NiceFileWidget, self).render(name, value, default_attrs)
        if value:
            import os
            val = os.path.basename(value.name)
            fn = '<div class="lib_nf_filename" style="background: url(%slib/fileinput/icons.png) no-repeat 0 -96px;"> %s </div>' % (settings.MEDIA_URL, val)
        else:
            fn = '<div class="lib_nf_filename" style="display:none;'\
                          ' background: url(%slib/fileinput/icons.png);"> </div>' % (settings.MEDIA_URL)
            
        output.append('<div class="lib_nf_wrapper">')
        output.append(standart)
        output.append('<div class="lib_nf_fakebutton"></div>')
        output.append('<div class="lib_nf_blocker"></div>')
        output.append('<div class="lib_nf_fakebutton lib_nf_activebutton"></div>')
        output.append(fn)
        output.append('</div>')
            
        print fn
        
        return mark_safe(u''.join(output))
    
    class Media:
        js = (
            settings.MEDIA_URL + 'lib/fileinput/input.js',
        )
        
        css = {
            'all': [settings.MEDIA_URL + 'lib/fileinput/input.css'],
        }