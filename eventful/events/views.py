from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (ListView, DetailView, CreateView, DeleteView, UpdateView, View,
                                  TemplateView)

from common.cache import decr_notification
from .decorators import user_is_event_author
from .forms import EventForm
from .models import Event, EventInvite


class EventDetail(DetailView):
    model = Event
    queryset = Event.objects.details()
    invited_by_status = {}
    user_invite_status = None

    def get_object(self, **kwargs):
        event = super().get_object(**kwargs)
        perm, invite = event.get_permission_and_invite(self.request.user)
        if not perm:
            raise PermissionDenied
        event.incr_views()
        setattr(event, 'user_invite', invite)
        return event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invite'] = self.object.user_invite
        invited_by_status = self.object.invited_by_status()

        for key, value in invited_by_status.items():
            context['invites_' + key] = value

        return context


class EventActionMixin:
    form_class = EventForm
    template_name = 'events/event_create_update.html'

    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, self.success_msg, extra_tags='Success')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event:detail', args=(self.object.pk, ))


@method_decorator(login_required, name='dispatch')
class EventCreate(EventActionMixin, CreateView):
    model = Event
    success_msg = 'Event created.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends'] = list(self.request.user.profile.get_friends())
        return context


@method_decorator(user_is_event_author, name='dispatch')
class EventUpdate(EventActionMixin, UpdateView):
    model = Event
    success_msg = 'Event updated.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['attend'] = self.object.self_invite_exist(self.request.user.pk)
        kwargs['update'] = True
        return kwargs


@method_decorator(user_is_event_author, name='dispatch')
class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('index')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted.', extra_tags='Success')
        return super().delete(request, *args, **kwargs)


class EventListView(ListView):
    context_object_name = 'events'
    paginate_by = 12
    privacy = Event.PUBLIC

    def get_queryset(self):
        return Event.objects.future_by_privacy(self.privacy, self.request.user)


class IndexView(EventListView):
    template_name = 'events/index.html'


class EventsPaginate(EventListView):
    def get_template_names(self):
        if self.request.is_ajax():
            return 'events/snippets/event_list_pagination.html'
        return 'events/events.html'


@method_decorator(login_required, name='dispatch')
class EventsFriends(EventsPaginate):
    def get_queryset(self):
        return Event.objects.friends_events(self.request.user)


class EventInviteAction(LoginRequiredMixin, View):
    http_method_names = [u'post']
    event_cls = None

    def manager_method(self, *args, **kwargs):
        raise NotImplementedError

    def get_event_object_or_pk(self, pk):
        if self.event_cls:
            try:
                return self.event_cls.objects.get(pk=pk)
            except self.event_cls.DoesNotExist:
                return
        else:
            return pk

    def get_post_value(self):
        return self.request.POST.get('pk')

    def post(self, request, pk):
        result = False
        obj_or_pk = self.get_event_object_or_pk(pk)
        if obj_or_pk:
            result = self.manager_method(obj_or_pk, request.user, self.get_post_value())
        return JsonResponse({'result': result})


class JoinEvent(EventInviteAction):
    event_cls = Event
    manager_method = EventInvite.objects.join


class AcceptEventInvite(EventInviteAction):
    manager_method = EventInvite.objects.accept


class RejectEventInvite(EventInviteAction):
    manager_method = EventInvite.objects.reject


class PendEventInvite(EventInviteAction):
    manager_method = EventInvite.objects.pend


class SelfRemoveEventInvite(EventInviteAction):
    manager_method = EventInvite.objects.self_remove


class RemoveEventInvite(EventInviteAction):
    manager_method = EventInvite.objects.remove


class Invite(EventInviteAction):
    event_cls = Event
    manager_method = EventInvite.objects.invite

    def get_post_value(self):
        return self.request.POST.getlist('pks[]')


class ShowEventInvites(LoginRequiredMixin, TemplateView):
    template_name = 'events/invites.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invites_grouped = EventInvite.objects.get_all_grouped(self.request.user)

        for key, value in invites_grouped.items():
            context[key] = value

        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        decr_notification('e_invites_count', request.user.pk)
        return response
