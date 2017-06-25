from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

from events.forms import EventForm
from events.models import Event


class EventDetail(DetailView):
    model = Event

    def get_object(self, **kwargs):
        event = super().get_object(**kwargs)
        event.views += 1
        event.save()
        return event


class EventActionMixin:
    form_class = EventForm
    template_name = 'events/event_create_update.html'

    @property
    def success_msg(self):
        return NotImplemented

    def form_valid(self, form):
        messages.success(self.request, self.success_msg, extra_tags='Success')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('events:detail', args=(self.object.pk, ))


class EventCreate(EventActionMixin, CreateView):
    model = Event
    success_msg = 'Event created.'


class EventUpdate(EventActionMixin, UpdateView):
    model = Event
    success_msg = 'Event updated.'


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
        return Event.objects.filter(privacy=self.privacy, start_date__gt=timezone.now())


class IndexView(EventListView):
    template_name = 'events/index.html'


class EventsPaginate(EventListView):
    def get_template_names(self):
        if self.request.is_ajax():
            return 'events/snippets/event_list_pagination.html'
        return 'events/events.html'


class EventsPrivate(EventsPaginate):
    privacy = Event.PRIVATE


class EventsFriends(EventsPaginate):
    privacy = Event.FRIENDS
