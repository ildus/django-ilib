#coding: utf-8

from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms import widgets
from tagging.utils import parse_tag_input

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
