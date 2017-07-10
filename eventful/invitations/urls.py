from django.conf.urls import url

from invitations import views


app_name = 'invitations'

urlpatterns = [
    url(r'^$', views.InvitationsList.as_view(), name='list'),
    url(r'^friends/$', views.ShowFriends.as_view(), name='friends'),
    url(r'^send_friend_request/$', views.SendFriendRequest.as_view(), name='send_friend_request'),
    url(r'^accept_friend_request/$', views.AcceptFriendRequest.as_view(), name='accept_friend_request'),
    url(r'^reject_friend_request/$', views.RejectFriendRequest.as_view(), name='reject_friend_request'),
]
