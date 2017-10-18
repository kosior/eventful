from django.core.exceptions import PermissionDenied
from django.urls import reverse
from pytest import raises

from events.decorators import user_is_event_author
from .factories import EventFactory, UserFactory


@user_is_event_author
def fn_to_test(request, *args, **kwargs):
    return True


def test_user_is_event_author_when_is_not_creator(rf):
    event = EventFactory()
    user = UserFactory()
    request = rf.get(reverse('event:detail', args=(event.pk,)))
    request.user = user

    with raises(PermissionDenied):
        fn_to_test(request, pk=event.pk)


def test_user_is_event_author_when_is_creator(rf):
    event = EventFactory()
    user = event.created_by
    request = rf.get(reverse('event:detail', args=(event.pk,)))
    request.user = user
    assert fn_to_test(request, pk=event.pk)
