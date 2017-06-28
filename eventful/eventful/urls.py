from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin

from events.views import IndexView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^events/', include('events.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^profile/(?P<username>[\w@.+-]{1,150})/', include('userprofiles.urls')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
