import pytz

from django.shortcuts import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.COOKIES.get('timezone')

        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

    def process_response(self, request, response):
        if request.user.is_authenticated and not request.session.get('timezone'):
            tz = request.user.profile.timezone
            request.session['timezone'] = tz
            response.set_cookie('timezone', tz, max_age=365 * 24 * 60 * 60)
        return response
