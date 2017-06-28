from functools import wraps

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied


def user_is_himself(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        user = User.objects.get(username=kwargs['username'])
        if request.user == user:
            return fn(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper
