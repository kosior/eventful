from django.conf.urls import url

from .. import views


app_name = 'event'

urlpatterns = [
    url(r'^$', views.EventDetail.as_view(), name='detail'),
    url(r'^delete/$', views.EventDelete.as_view(), name='delete'),
    url(r'^update/$', views.EventUpdate.as_view(), name='update'),
    url(r'^accept/$', views.AcceptEventInvite.as_view(), name='accept'),
    url(r'^join/$', views.JoinEvent.as_view(), name='join'),
    url(r'^pend/$', views.PendEventInvite.as_view(), name='pend'),
    url(r'^reject/$', views.RejectEventInvite.as_view(), name='reject'),
    url(r'^self_remove/$', views.SelfRemoveEventInvite.as_view(), name='self_remove'),
    url(r'^remove/$', views.RemoveEventInvite.as_view(), name='remove'),
    url(r'^invite/$', views.Invite.as_view(), name='invite'),
]
