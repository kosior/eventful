from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.timezone import now, timedelta
from pytest import raises

from events import views
from events.models import Event, EventInvite
from .factories import EventFactory, UserFactory, FriendshipFactory


class TestEventDetail:
    url_name = 'event:detail'

    def test_when_no_event(self, client):
        response = client.get(reverse(self.url_name, args=(123,)))
        assert response.status_code == 404

    def test_when_event_is_public(self, client):
        event = EventFactory(description='Test description')
        response = client.get(reverse(self.url_name, args=(event.pk,)))
        assert response.status_code == 200
        assert response.context['event'] == event
        assert event.title, event.description in response.content.decode()

    def test_event_public_request_from_event_creator(self, rf):
        event = EventFactory()
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = event.created_by
        response = views.EventDetail.as_view()(request, pk=event.pk)
        assert response.status_code == 200

    def test_event_friends_request_from_event_creator(self, rf):
        event = EventFactory(privacy=Event.FRIENDS)
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = event.created_by
        response = views.EventDetail.as_view()(request, pk=event.pk)
        assert response.status_code == 200

    def test_event_private_request_from_event_creator(self, rf):
        event = EventFactory(privacy=Event.PRIVATE)
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = event.created_by
        response = views.EventDetail.as_view()(request, pk=event.pk)
        assert response.status_code == 200

    def test_when_event_for_friends_or_private_and_user_is_anonymous(self, client):
        event1 = EventFactory(privacy=Event.FRIENDS)
        event2 = EventFactory(privacy=Event.PRIVATE)
        response1 = client.get(reverse(self.url_name, args=(event1.pk,)))
        response2 = client.get(reverse(self.url_name, args=(event2.pk,)))
        assert response1.status_code == 403
        assert response2.status_code == 403

    def test_when_user_invited(self, rf):
        event1 = EventFactory(privacy=Event.FRIENDS)
        event2 = EventFactory(privacy=Event.PRIVATE)
        user1 = UserFactory(get_invited_to=event1)
        user2 = UserFactory(get_invited_to=event2)
        request1 = rf.get(reverse(self.url_name, args=(event1.pk,)))
        request1.user = user1
        request2 = rf.get(reverse(self.url_name, args=(event2.pk,)))
        request2.user = user2
        response1 = views.EventDetail.as_view()(request1, pk=event1.pk)
        response2 = views.EventDetail.as_view()(request2, pk=event2.pk)
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_events_for_friends_when_friendship(self, rf):
        event = EventFactory(privacy=Event.FRIENDS)
        user = UserFactory()
        FriendshipFactory(to_user=user, from_user=event.created_by)
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = user
        response = views.EventDetail.as_view()(request, pk=event.pk)
        assert response.status_code == 200

    def test_events_for_friends_when_no_friendship(self, rf):
        event = EventFactory(privacy=Event.FRIENDS)
        user = UserFactory()
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = user
        with raises(PermissionDenied):
            views.EventDetail.as_view()(request, pk=event.pk)

    def test_if_views_incremented(self, client):
        event = EventFactory()
        assert event.views == 0
        client.get(reverse(self.url_name, args=(event.pk,)))
        event.refresh_from_db()
        assert event.views == 1

    def test_if_user_invite_in_event(self, rf):
        event = EventFactory(privacy=Event.PRIVATE)
        user = UserFactory(get_invited_to=event)
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = user
        response = views.EventDetail.as_view()(request, pk=event.pk)
        invite = response.context_data['event'].user_invite
        assert invite.to_user == user
        assert invite.status == EventInvite.PENDING

    def test_if_user_invite_in_event_when_self_invite(self, rf):
        event = EventFactory(join=True)
        request = rf.get(reverse(self.url_name, args=(event.pk,)))
        request.user = event.created_by
        response = views.EventDetail.as_view()(request, pk=event.pk)
        invite = response.context_data['event'].user_invite
        assert invite.to_user == event.created_by
        assert invite.from_user == event.created_by
        assert invite.status == EventInvite.SELF

    def test_if_invties_present_in_context(self, client):
        event = EventFactory(join=True)
        users = [UserFactory(get_invited_to=event) for _ in range(3)]
        EventInvite.objects.accept(event.pk, users[0])
        EventInvite.objects.reject(event.pk, users[1])
        response = client.get(reverse(self.url_name, args=(event.pk,)))
        assert response.context['invites_self'][0] == event.created_by
        assert response.context['invites_accepted'][0] == users[0]
        assert response.context['invites_rejected'][0] == users[1]
        assert response.context['invites_pending'][0] == users[2]


class TestEventActionMixin:
    def test_succes_msg(self):
        obj = views.EventActionMixin()
        assert obj.success_msg == NotImplemented


class TestEventCreate:
    url_view = 'events:create'

    @staticmethod
    def add_middleware_to_response(request, middleware_classes):
        [m_class().process_request(request) for m_class in middleware_classes]
        return request

    def test_access(self, rf):
        user1 = AnonymousUser()
        user2 = UserFactory()
        request = rf.get(reverse(self.url_view))
        request.user = user1
        response = views.EventCreate.as_view()(request)
        assert response.status_code == 302
        assert '/accounts/login/' in response.url
        request.user = user2
        response = views.EventCreate.as_view()(request)
        assert response.status_code == 200

    def test_if_friends_in_context(self, rf):
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()
        FriendshipFactory(from_user=user1, to_user=user2)
        FriendshipFactory(from_user=user1, to_user=user3)
        request = rf.get(reverse(self.url_view))
        request.user = user1
        response = views.EventCreate.as_view()(request)
        assert len(response.context_data['friends']) == 2

    def test_post(self, rf):
        data = {
            'title': 'Test title',
            'description': '',
            'privacy': Event.PUBLIC,
            'start_date': (now() + timedelta(hours=24)).strftime('%d.%m.%Y %H:%M'),
            'attend': False,
            'invite': []
        }
        user = UserFactory()
        request = rf.post(reverse(self.url_view), data)
        self.add_middleware_to_response(request, (SessionMiddleware, MessageMiddleware))
        request.user = user
        response = views.EventCreate.as_view()(request)
        assert response.status_code == 302
        pk = int(response.url.split('/')[-2])
        assert Event.objects.get(pk=pk).title == 'Test title'
