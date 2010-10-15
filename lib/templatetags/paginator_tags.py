# -*- coding: UTF-8 -*-
from django import template
register = template.Library()

@register.inclusion_tag("lib/widget/paginator.html", takes_context=True)
def paginator(context):
    return context
