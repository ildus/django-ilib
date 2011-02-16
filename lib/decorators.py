# coding: utf-8

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

def render_with_requestcontext(func):
    def my_render_function(request, *args, **kwargs):
        """ rendering with RequestContext """
        
        template, data = func(request, *args, **kwargs)
        context = RequestContext(request, data)
        return render_to_response(template, context_instance=context)
    
    return my_render_function

def render_with_processor(processor = None):
    def wrapper(func):
        """ rendering with RequestContext and processor """
        
        def my_render_function(request, *args, **kwargs):
            template, data = func(request, *args, **kwargs)
            context = RequestContext(request, data, [processor])
            return render_to_response(template, context_instance=context)
        
        return my_render_function
    
    return wrapper

def login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(request, *args, **kwargs)
        else:
            if request.is_ajax():
                result = {'success': False, 'error': _('Authorization required')}
                json = simplejson.dumps(result)
                return HttpResponseForbidden(json, mimetype = 'text/plain')
            else:
                return redirect('login_wrapper')
    
    return wrapper

def paginate_by(items_key, count):
    ''' Разделяет на страницы, работает совместнго с тегом paginator '''
    def pager(func):
        def wrapper(request, *args, **kwargs):
            all_data = func(request, *args, **kwargs)
            paginator = Paginator(all_data[1][items_key], count)
    
            try:
                page_number = int(request.GET.get('page', '1'))
            except ValueError:
                page_number = 1
        
            try:
                page = paginator.page(page_number)
            except (EmptyPage, InvalidPage):
                page = paginator.page(paginator.num_pages)
                
            all_data[1]['page'] = page
            all_data[1]['page_number'] = page_number
            all_data[1][items_key] = page.object_list
            
            return all_data
    
        return wrapper
    
    return pager
