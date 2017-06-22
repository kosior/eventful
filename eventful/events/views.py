from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, DeleteView

from events.forms import CreateEventForm
from events.models import Event


class EventDetail(DetailView):
    model = Event

    def get_object(self, **kwargs):
        event = super(EventDetail, self).get_object(**kwargs)
        event.views += 1
        event.save()
        return event


class EventCreate(CreateView):
    form_class = CreateEventForm
    template_name = 'events/event_create.html'

    def get_success_url(self):
        return reverse('events:detail', args=(self.object.pk, ))


class EventDelete(DeleteView):
    model = Event
    success_url = reverse_lazy('index')


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
