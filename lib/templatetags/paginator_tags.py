# -*- coding: UTF-8 -*-
from django import template
register = template.Library()

@register.inclusion_tag("lib/widget/paginator.html", takes_context=True)
def paginator(context):
    return context

ON_EACH_SIDE = 3
ON_ENDS = 2
DOT = '.'

@register.inclusion_tag("admin/inline/paginator.html")
def admin_inline_paginator(cl):
    paginator = cl.paginator
    page = cl.page_num + 1
    
    if paginator.num_pages <=  20:
        page_range = range(paginator.num_pages)
    else:
        page_range = []
        if page > (ON_EACH_SIDE  + ON_ENDS):
            page_range.extend(range(0, ON_EACH_SIDE  - 1))
            page_range.append(DOT)
            if page < paginator.num_pages:
                page_range.extend(range(page - ON_EACH_SIDE, page+1))
            else:
                page_range.extend(range(page - ON_EACH_SIDE, page))
        else:
            page_range.extend(range(0, page  + 1))
        
        if page < (paginator.num_pages -  ON_EACH_SIDE - ON_ENDS - 1):
            page_range.extend(range(page + 1, page +  ON_EACH_SIDE + 1))
            page_range.append(DOT)
            page_range.extend(range(paginator.num_pages  - ON_ENDS,  paginator.num_pages))
        else:
            page_range.extend(range(page + 1, paginator.num_pages))
    
    return locals()