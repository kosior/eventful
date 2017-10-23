import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from common.utils import get_user_timezone


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = get_user_timezone(request)
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

    def process_response(self, request, response):
        if request.user.is_authenticated and not request.session.get('visited'):
            request.session['visited'] = True
            tz = request.user.profile.timezone
            request.session['timezone'] = tz
            response.set_cookie('timezone', tz, max_age=365 * 24 * 60 * 60)
        elif not request.COOKIES.get('timezone'):
            tz = request.session.get('timezone')
            response.set_cookie('timezone', tz, max_age=365 * 24 * 60 * 60)
        return response
