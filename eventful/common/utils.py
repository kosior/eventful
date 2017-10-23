import requests


class IPUserInfo:
    user_info = None
    _ip = None

    def __init__(self, request):
        self.request = request

    @property
    def ip(self):
        if self._ip is None:
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                self._ip = x_forwarded_for.split(',')[0]
            else:
                self._ip = self.request.META.get('REMOTE_ADDR')
        return self._ip

    def _get_data_from_freegeoip(self):
        if self.ip:
            url = f'https://freegeoip.net/json/{self.ip}'
            try:
                response = requests.get(url, timeout=2)
            except requests.exceptions.Timeout:
                return {}
            else:
                if response.status_code == 200:
                    return response.json()
        return {}

    def _get_value(self, key, default=''):
        if self.user_info is None:
            self.user_info = self._get_data_from_freegeoip()
        return self.user_info.get(key, default)

    @property
    def timezone(self):
        return self._get_value('time_zone', default='')


def get_user_timezone(request):
    timezone = request.COOKIES.get('timezone') or request.session.get('timezone')
    if timezone:
        return timezone
    timezone = IPUserInfo(request).timezone
    request.session['timezone'] = timezone
    return timezone
