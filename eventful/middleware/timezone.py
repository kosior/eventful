import pytz

from django.shortcuts import reverse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.COOKIES.get('timezone')

        if request.user.is_authenticated:
            profile_tz = request.user.profile.timezone
            if profile_tz:
                tzname = profile_tz

        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()

    def process_response(self, request, response):
        referer = request.META.get('HTTP_REFERER', '')
        url_list = [reverse('account_login'), reverse('account_signup')]
        if request.user.is_authenticated and any(url in referer for url in url_list):
            response.set_cookie('timezone', request.user.profile.timezone, max_age=365*24*60*60)
        return response
