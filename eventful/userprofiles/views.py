from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, UpdateView, TemplateView

from userprofiles.decorators import user_is_himself
from userprofiles.forms import UserProfileForm
from userprofiles.models import UserProfile
from userprofiles.utils import get_timezones

from invitations.models import FriendInvitation


class ProfileDetail(DetailView):
    model = User
    context_object_name = 'requested_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'userprofiles/profile_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = self.object.created_events.all()

        if self.request.user == self.object:
            event_groups = {'PB': [], 'PR': [], 'FR': []}
            for event in events:
                event_groups[event.privacy].append(event)
            context['events_pb'] = event_groups['PB']
            context['events_pr'] = event_groups['PR']
            context['events_fr'] = event_groups['FR']
        else:
            context['events'] = events.filter(privacy='PB')
            context['invite_status'] = FriendInvitation.objects.get_invite_status(from_user=self.request.user,
                                                                                  to_user=self.object)
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


class SetTimezone(TemplateView):
    def get_template_names(self):
        if self.request.is_ajax():
            return 'userprofiles/snippets/timezone_picker_select_form.html'
        return 'userprofiles/set_timezone.html'

    def get(self, request, *args, **kwargs):
        tz = request.GET.get('timezone')
        context = self.get_context_data(tz)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        tz = request.POST.get('timezone')
        if request.user.is_authenticated:
            user_profile = request.user.profile
            user_profile.timezone = tz
            user_profile.save()
        redirect_to = request.POST.get('redirect_to')
        response = redirect(redirect_to)
        response.set_cookie('timezone', tz)
        messages.success(request, 'Timezone set to: {}'.format(tz))
        return response

    def get_context_data(self, tz, **kwargs):
        context = super().get_context_data(**kwargs)
        timezones_suggested, timezones_other = get_timezones(tz)
        context.update({'timezones_suggested': timezones_suggested,
                        'timezones_other': timezones_other})
        return context
