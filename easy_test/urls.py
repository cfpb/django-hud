from django.conf.urls import patterns, url

from easy_test import views

urlpatterns = patterns('',
    url( r'^$', views.show_index )
)
