#coding: utf-8

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^img/(\d+)/$', 'lib.views.img_redirect', name='img_redirect'),
    url(r'^get_fk_data/(\d+)/([\w_0-9]+)/$', 
        'lib.fields.special.dojo_foreign.fk_field_data', name='fk_field_data'),
    url(r'^get_fk_data/(\d+)/([\w_0-9]+)/([\w_0-9]+)/$', 
        'lib.fields.special.dojo_foreign.fk_field_data', name='fk_field_data_with_node'),
    url(r'^fk_select/$', 
        'lib.fields.special.dojo_foreign.fk_select', name='fk_select'),
    url(r'^fk_listselect/(\d+)/([\w_0-9]+)/$', 
        'lib.fields.special.dojo_foreign.fk_listselect', name='fk_listselect'),
)