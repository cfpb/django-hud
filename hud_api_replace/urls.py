from django.conf.urls import patterns, url

from hud_api_replace import views

urlpatterns = patterns('',
    url(r'^(?P<zipcode>\d{5})/$', views.api_entry, name='index'),
    url(r'^(?P<zipcode>\d{5})\.(?P<output_format>\w+)/$', views.api_entry, name='index'),
)
