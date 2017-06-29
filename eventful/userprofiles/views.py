from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, UpdateView

from userprofiles.decorators import user_is_himself
from userprofiles.forms import UserProfileForm
from userprofiles.models import UserProfile


class ProfileDetail(DetailView):
    model = User
    context_object_name = 'requested_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'userprofiles/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datetime_now'] = timezone.now()
        events = self.object.created_events.filter()

        if self.request.user == self.object:
            event_groups = {'PB': [], 'PR': [], 'FR': []}
            for event in events:
                event_groups[event.privacy].append(event)
            context['events_pb'] = event_groups['PB']
            context['events_pr'] = event_groups['PR']
            context['events_fr'] = event_groups['FR']
        else:
            context['events'] = events.filter(privacy='PB')
        return context


@method_decorator(user_is_himself, name='dispatch')
class ProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_success_url(self):
        return reverse('userprofiles:profile', args=(self.kwargs.get('username'), ))
