# coding: utf-8
from django.contrib import admin
from lib.models import SimpleImage
from django.conf import settings
from sorl.thumbnail.main import DjangoThumbnail
from django.utils.translation import ugettext_lazy as _

class ImageAdmin(admin.ModelAdmin):
    list_display=('description', 'thumbnail', 'filename')
    search_fields = ('description', 'filename', )
    list_filter = ('extension', )
    
    def thumbnail(self, obj):
        thumbnail = DjangoThumbnail(obj.image, (150, 150))
        return u'<img src="%s" border="0" alt="" width="%s" height="%s" />' % \
                            (thumbnail.absolute_url,
                             thumbnail.width(), thumbnail.height())
    thumbnail.short_description = _('image')
    thumbnail.allow_tags = True
    
    class Media:
        js = (
            settings.MEDIA_URL+'lib/js/richeditor_img_uploader.js',
        )

admin.site.register(SimpleImage, ImageAdmin)
