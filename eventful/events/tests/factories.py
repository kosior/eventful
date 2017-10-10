import factory
from django.contrib.auth.models import User
from django.utils import timezone

from events.models import Event


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    password = 'pass'


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    created_by = factory.SubFactory(UserFactory)
    title = 'Event title'
    start_date = timezone.now() + timezone.timedelta(hours=24)
