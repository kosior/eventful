from django.utils import timezone
from django.views.generic import ListView

from events.models import Event


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
