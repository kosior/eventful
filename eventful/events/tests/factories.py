import factory
from django.contrib.auth.models import User
from django.utils import timezone

from events.models import Event, EventInvite
from userprofiles.models import FriendRequest


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        join_event = None
        get_invited_to = None
        friend_user = None

    @classmethod
    def create(cls, **kwargs):
        obj = super().create(**kwargs)
        join_event = kwargs.get('join_event')
        get_invited_to = kwargs.get('get_invited_to')
        friend_user = kwargs.get('friend_user')
        if isinstance(join_event, Event):
            EventInvite.objects.join(join_event, obj, check_perm=False)
        elif isinstance(get_invited_to, Event):
            from_user = get_invited_to.created_by
            EventInvite.objects.invite(get_invited_to, from_user, obj.pk)
        if friend_user:
            FriendRequest.objects.send_friend_request(friend_user, obj.pk)
            FriendRequest.objects.accept(obj, friend_user.pk)
        return obj

    username = factory.Sequence(lambda n: f'user{n}')
    password = 'pass'


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    class Params:
        past_or_future = 'future'
        join = False

    @classmethod
    def create(cls, **kwargs):
        obj = super().create(**kwargs)
        if kwargs.get('join'):
            EventInvite.objects.join(obj, obj.created_by)
        return obj

    @staticmethod
    def _get_date_time(obj):
        if obj.past_or_future == 'future':
            return timezone.now() + timezone.timedelta(hours=24)
        elif obj.past_or_future == 'past':
            return timezone.now() - timezone.timedelta(hours=24)

    created_by = factory.SubFactory(UserFactory)
    title = 'Event title'
    start_date = factory.LazyAttribute(lambda o: EventFactory._get_date_time(o))
