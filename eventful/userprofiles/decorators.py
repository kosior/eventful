from functools import wraps

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied


def user_is_himself(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        if request.user.username == kwargs['username']:
            return fn(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrapper
