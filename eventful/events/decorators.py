from functools import wraps

from django.core.exceptions import PermissionDenied

from events.models import Event


def user_is_event_author(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        event = Event.objects.get(pk=kwargs['pk'])
        if request.user == event.created_by:
            return fn(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper
