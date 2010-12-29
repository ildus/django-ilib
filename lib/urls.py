#coding: utf-8

from django.conf.urls.defaults import patterns, url

#popup
urlpatterns = patterns('lib.fields.popup.foreign_key',    
    url(r'^get_fk_data/(\d+)/([\w_0-9]+)/$', 'fk_field_data', name='fk_field_data'),
    url(r'^get_fk_data/(\d+)/([\w_0-9]+)/([\w_0-9]+)/$', 'fk_field_data', name='fk_field_data_with_node'),
    url(r'^fk_select/$', 'fk_select', name='fk_select'),
    url(r'^fk_listselect/(\d+)/([\w_0-9]+)/$', 'fk_listselect', name='fk_listselect'),
    url(r'^fk_listselect/(\d+)/([\w_0-9]+)/(\d+)/$', 'fk_listselect', name='fk_listselect_related'),    
)

#lib.views
urlpatterns += patterns('lib.views',
    url(r'^fk_related_values/$', 'get_related_values', name='fk_related_values'),
    url(r'^img/(\d+)/$', 'img_redirect', name='img_redirect'),
)