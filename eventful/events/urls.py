from django.conf.urls import url

from events import views


app_name = 'events'

urlpatterns = [
    url(r'^(?P<pk>[\d]+)$', views.EventDetail.as_view(), name='detail'),
    url(r'^public/$', views.EventsPaginate.as_view(), name='public'),
    url(r'^private/$', views.EventsPrivate.as_view(), name='private'),
    url(r'^friends/$', views.EventsFriends.as_view(), name='friends'),
]
