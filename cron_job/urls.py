from django.conf.urls import patterns, url

from cron_job import views

urlpatterns = patterns('',
    url( r'^load-hud-data/$', views.load_hud_data, name = 'index'),
)
