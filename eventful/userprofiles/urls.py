from django.conf.urls import url

from userprofiles.views import ProfileDetail, ProfileUpdate


app_name = 'userprofiles'

urlpatterns = [
    url(r'^$', ProfileDetail.as_view(), name='profile'),
    url(r'^update/$', ProfileUpdate.as_view(), name='update'),
]
