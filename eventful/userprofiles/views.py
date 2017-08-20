from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Prefetch, F
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, UpdateView, TemplateView, ListView, View

from .decorators import user_is_himself
from .forms import UserProfileForm
from .models import UserProfile, FriendRequest
from .utils import get_timezones


class ProfileDetail(DetailView):
    model = User
    context_object_name = 'requested_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'userprofiles/profile_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        prefetch_queryset = UserProfile.objects.select_related('user').only('user__username')
        return queryset.select_related('profile').prefetch_related(
            Prefetch('profile__friends', queryset=prefetch_queryset)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = self.object.created_events.all()
        context['datetime_now'] = timezone.now()

        if self.request.user == self.object:
            event_groups = {'PB': [], 'PR': [], 'FR': []}
            for event in events:
                event_groups[event.privacy].append(event)
            context['events_pb'] = event_groups['PB']
            context['events_pr'] = event_groups['PR']
            context['events_fr'] = event_groups['FR']
        else:
            context['events'] = events.filter(privacy='PB')
            if self.object.profile.are_friends(self.request.user.pk):
                context['are_friends'] = True
            else:
                friend_request = FriendRequest.objects.get_with_related(self.request.user,
                                                                        self.object.pk)
                context['friend_request'] = friend_request
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
            request.session['timezone'] = tz
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


class ShowFriends(LoginRequiredMixin, ListView):
    context_object_name = 'friends'
    template_name = 'userprofiles/friends.html'

    def get_queryset(self):
        return self.request.user.profile.friends.select_related('user').only('user_id',
                                                                           'user__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grouped_requests = FriendRequest.objects.get_all_grouped(self.request.user)
        context['pending'] = grouped_requests.get('pending')
        context['sent'] = grouped_requests.get('sent')
        return context


class InvitationActionMixin(LoginRequiredMixin):
    http_method_names = [u'post']

    def post(self, request, **kwargs):
        args = (request.user, int(request.POST.get('pk')))
        result = self.manager_method(*args)
        return JsonResponse({'result': result})


class SendFriendRequest(InvitationActionMixin, View):
    manager_method = FriendRequest.objects.send_friend_request


class AcceptFriendRequest(InvitationActionMixin, View):
    manager_method = FriendRequest.objects.accept


class RejectFriendRequest(InvitationActionMixin, View):
    manager_method = FriendRequest.objects.reject


class RemoveFriend(InvitationActionMixin, View):
    manager_method = FriendRequest.objects.remove_friend


class GetFriends(View):
    http_method_names = [u'get']

    def get(self, request, username):
        user_profile = UserProfile.objects.filter(user__username=username).first()
        friends = user_profile.get_friends()
        return JsonResponse(list(friends), safe=False)
