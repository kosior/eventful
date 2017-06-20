from django.conf.urls import url

from events.views import EventsPaginate, EventsPrivate, EventsFriends


app_name = 'events'

urlpatterns = [
    url(r'^public/$', EventsPaginate.as_view(), name='public'),
    url(r'^private/$', EventsPrivate.as_view(), name='private'),
    url(r'^friends/$', EventsFriends.as_view(), name='friends'),
]
