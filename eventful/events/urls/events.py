from django.conf.urls import url

from .. import views


app_name = 'events'

urlpatterns = [
    url(r'^create/$', views.EventCreate.as_view(), name='create'),
    url(r'^public/$', views.EventsPaginate.as_view(), name='public'),
    url(r'^friends/$', views.EventsFriends.as_view(), name='friends'),
    url(r'^invites/$', views.ShowEventInvites.as_view(), name='invites'),
]
