#coding: utf-8

from django.db import models
from lib.utils import make_upload_path, is_generic_filename
from django.utils.translation import ugettext_lazy as _

class SimpleImage(models.Model):
    ''' Модель картинки, изпользуется для загрузки изображений в различные редакторы '''
    
    filename = models.CharField(_('filename'), max_length = 300, editable = False)
    extension = models.CharField(_('extension'), max_length = 10, editable = False)
    image = models.ImageField(upload_to=make_upload_path,verbose_name=_('image'))
    description = models.CharField(_('description'), max_length = 300)
    
    def __unicode__(self):
        return "%s: %s"% (self.description, self.filename)
    
    def save(self):
        import os
        if not is_generic_filename(self.filename):
            self.filename = os.path.basename(self.image.name)
            self.extension = os.path.splitext(self.filename)[1]
        super(SimpleImage, self).save()
        
    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
