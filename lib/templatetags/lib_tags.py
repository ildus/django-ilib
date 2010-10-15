# -*- coding:utf-8 -*-

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.conf import settings

register=template.Library()

class PaginatorNode(template.Node):
    def render(self,context):
        page=context['page']
        page_number=context['page_number']
        class_name='paginator'
        next_text='дальше →'
        previous_text='← назад'
        if page.has_next():
            next_link='<a href="?page=%s" class="next">%s</a> '%(page_number+1,next_text)
        else:
            next_link=''

        if page.has_previous():
            previous_link='<a href="?page=%s" class="previous">%s</a> '%(page_number-1,previous_text)
        else:
            previous_link=''

        if next_link or previous_link:
            return '<div class="%s">%s %s</div>'%(class_name,previous_link,next_link)
        else:
            return ''

@register.tag
def paginator(parser, token):
    '''
    Выводит навигатор по страницам.

    В контексте должны находиться переменные "page" с объектом
    paginator'а и "page_number" с номером страницы (счет с 1).
    '''
    return PaginatorNode()

@register.inclusion_tag('admin/inline_table_filters.html')
def lib_list_filter(cl, spec):
    return {'spec': spec, 'title': spec.title(), 'choices' : list(spec.choices(cl))}

