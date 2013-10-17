from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_hud.views.home', name='home'),
    # url(r'^django_hud/', include('django_hud.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^hud-api-replace/', include('hud_api_replace.urls')),
    url(r'^cron-job/', include('cron_job.urls')),
    url(r'^easy-test/', include('easy_test.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
