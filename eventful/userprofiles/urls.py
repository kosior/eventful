from django.conf.urls import url

from . import views


app_name = 'userprofiles'

urlpatterns = [
    url(r'^$', views.ProfileDetail.as_view(),
        name='profile'),
    url(r'^update/$', views.ProfileUpdate.as_view(),
        name='update'),
    url(r'^friends/$', views.ShowFriends.as_view(),
        name='friends'),
    url(r'^send_friend_request/$', views.SendFriendRequest.as_view(),
        name='send_friend_request'),
    url(r'^accept_friend_request/$', views.AcceptFriendRequest.as_view(),
        name='accept_friend_request'),
    url(r'^reject_friend_request/$', views.RejectFriendRequest.as_view(),
        name='reject_friend_request'),
    url(r'^remove_friend/$', views.RemoveFriend.as_view(),
        name='remove_friend'),
    url(r'^get_friends/$', views.GetFriends.as_view(),
        name='get_friends'),
]
