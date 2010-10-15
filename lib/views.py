#coding: utf-8

from django.shortcuts import redirect, get_object_or_404
from models import SimpleImage
from django.conf import settings
import os

def img_redirect(request, image_id):
    image_obj = get_object_or_404(SimpleImage, pk = image_id)
    url = image_obj.image.name
    
    return redirect(os.path.join(settings.MEDIA_URL,url))
