from functools import wraps

from django.core.exceptions import PermissionDenied

from events.models import Event
from events.utils import is_user_an_author


def user_is_event_author(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        event = Event.objects.get(pk=kwargs['pk'])
        if is_user_an_author(request, event):
            return fn(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper
