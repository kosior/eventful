from django.contrib.auth.models import User
from django.views.generic import DetailView, UpdateView
from django.urls import reverse
from django.utils.decorators import method_decorator

from userprofiles.decorators import user_is_himself
from userprofiles.models import UserProfile
from userprofiles.forms import UserProfileForm


class ProfileDetail(DetailView):
    model = User
    context_object_name = 'requested_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'userprofiles/profile_detail.html'


@method_decorator(user_is_himself, name='dispatch')
class ProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.kwargs.get('username')).profile

    def get_success_url(self):
        return reverse('userprofiles:profile', args=(self.kwargs.get('username'), ))
