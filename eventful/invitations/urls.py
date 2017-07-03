from django.conf.urls import url

from invitations import views


app_name = 'invitations'

urlpatterns = [
    url(r'^friend/$', views.SendFriendRequest.as_view(), name='send_friend_request'),
]
