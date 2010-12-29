#coding: utf-8

from django.shortcuts import redirect, get_object_or_404
from models import SimpleImage
from django.conf import settings
import os
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import simplejson

def img_redirect(request, image_id):
    image_obj = get_object_or_404(SimpleImage, pk = image_id)
    url = image_obj.image.name
    
    return redirect(os.path.join(settings.MEDIA_URL,url))

def get_related_values(request):
    if request.user.is_authenticated():
        content_type_id, field_name, field_value = request.POST['content_type_id'], request.POST['related_field'], request.POST['value']
        
        kwargs = {}
        kwargs[field_name] = field_value
        content_type = get_object_or_404(ContentType, pk = content_type_id)
        model = content_type.model_class()
        objects = model._default_manager.filter(**kwargs)
        result = [{'id': 0, 'title': '---------'}]+[{'id': obj.pk, 'title': unicode(obj)} for obj in objects]
        return HttpResponse(simplejson.dumps(result), mimetype = 'application/json')
    else:
        return HttpResponseForbidden('Need auth')