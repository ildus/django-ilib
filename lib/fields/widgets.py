#coding: utf-8

from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms import widgets
from tagging.utils import parse_tag_input
from popup.foreign_key import ForeignKeyListWidget, ForeignKeyTreeWidget
from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode
from django.forms.util import flatatt

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
        
#выдрано из  django 1.3 beta
class CheckboxInput(widgets.Widget):
    def __init__(self, attrs=None, check_test=bool):
        super(CheckboxInput, self).__init__(attrs)
        # check_test is a callable that takes a value and returns True
        # if the checkbox should be checked for that value.
        self.check_test = check_test

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, type='checkbox', name=name)
        try:
            result = self.check_test(value)
        except: # Silently catch exceptions
            result = False
        if result:
            final_attrs['checked'] = 'checked'
        if value not in ('', True, False, None):
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

    def value_from_datadict(self, data, files, name):
        if name not in data:
            # A missing value means False because HTML form submission does not
            # send results for unselected checkboxes.
            return False
        value = data.get(name)
        # Translate true and false strings to boolean values.
        values =  {'true': True, 'false': False}
        if isinstance(value, basestring):
            value = values.get(value.lower(), value)
        return value

    def _has_changed(self, initial, data):
        # Sometimes data or initial could be None or u'' which should be the
        # same thing as False.
        return bool(initial) != bool(data)
    
FILE_INPUT_CONTRADICTION = object()
        
class NiceFileWidget(widgets.FileInput):        
    def clear_checkbox_name(self, name):
        return name + '-clear'

    def clear_checkbox_id(self, name):
        return name + '_id'

    def render(self, name, value, attrs=None):
        output = []
        default_attrs = {
            'class': 'lib_nf_custom',
        }
        default_attrs.update(attrs)
        input_file = super(NiceFileWidget, self).render(name, value, default_attrs)
        if value:
            import os
            val = os.path.basename(value.name)
            try:
                ext = os.path.splitext(val)[1][1:]
            except:
                ext = 'null'
            if ext in ('mp3', 'mp2', 'ogg', 'wav'):
                icon = '96'
            elif ext in ('jpeg', 'jpg'):
                icon = '32'
            elif ext in ('png', ):
                icon = '48'
            elif ext in ('gif', ):
                icon = '64'
            else:
                icon = '176'
            fn = '<div class="lib_nf_filename" style="background: url(%slib/fileinput/icons.png) no-repeat 0 -%spx;"> %s <a href="#"></a> </div>' % (settings.MEDIA_URL, icon, val)
        else:
            fn = '<div class="lib_nf_filename" style="display:none;'\
                          ' background: url(%slib/fileinput/icons.png);"> </div>' % (settings.MEDIA_URL)
            
        output.append('<div class="lib_nf_wrapper">')
        output.append(input_file)
        output.append('<div class="lib_nf_fakebutton"></div>')
        output.append('<div class="lib_nf_blocker"></div>')
        output.append('<div class="lib_nf_fakebutton lib_nf_activebutton"></div>')
        output.append(fn)
        
        checkbox_name = self.clear_checkbox_name(name)
        checkbox_id = self.clear_checkbox_id(checkbox_name)
        clear_input = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
        output.append(clear_input)
        
        output.append('</div>')
        
        return mark_safe(u'\n'.join(output))
    
    def value_from_datadict(self, data, files, name):
        upload = super(NiceFileWidget, self).value_from_datadict(data, files, name)
        if CheckboxInput().value_from_datadict(data, files, self.clear_checkbox_name(name)):
            if upload:
                # If the user contradicts themselves (uploads a new file AND
                # checks the "clear" checkbox), we return a unique marker
                # object that FileField will turn into a ValidationError.
                return FILE_INPUT_CONTRADICTION
            # False signals to clear any existing value, as opposed to just None
            return False
        return upload
    
    class Media:
        js = (
            settings.MEDIA_URL + 'lib/fileinput/input.js',
        )
        
        css = {
            'all': [settings.MEDIA_URL + 'lib/fileinput/input.css'],
        }