import json
import os

import pytz
from django.conf import settings
from django.contrib.auth.models import User

from events.models import Event, EventInvite
from .models import FriendRequest

# abbreviation to timezones
abbr_to_tz = os.path.join(settings.STATIC_DIR, 'tz', 'abbr_to_tz.json')

# timezone to abbreviations
tz_to_abbr = os.path.join(settings.STATIC_DIR, 'tz', 'tz_to_abbr.json')


def get_json_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def get_timezones(tz_abbr):
    timezones_suggested = []
    timezones_other = []
    if tz_abbr:
        timezones_suggested = get_json_from_file(abbr_to_tz).get(tz_abbr, [])

    for tz in pytz.common_timezones:
        if tz in timezones_suggested:
            continue
        timezones_other.append(tz)
    return timezones_suggested, timezones_other


def offset_to_gmt(offset):
    pm = {'+': '-', '-': '+'}
    tz = 'Etc/GMT{}'.format(pm[offset[0]])
    offset = offset[2] if offset[1] == '0' else offset[1:3]
    return tz + offset


def check_timezone_abbr(abbr, offset):
    try:
        pytz.timezone(abbr)
    except pytz.exceptions.UnknownTimeZoneError:
        return offset_to_gmt(offset)
    else:
        return abbr


# for demonstration purposes only
def send_invites(pk):
    try:
        admin = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin = None
    else:
        FriendRequest.objects.send_friend_request(from_user=admin, to_user_pk=pk)

    try:
        event = Event.objects.get(pk=1)
    except Event.DoesNotExist:
        pass
    else:
        if admin:
            EventInvite.objects.invite(event=event, user=admin, pk_or_pks=pk)
