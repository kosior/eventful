from ..models import EventInvite, Event
from userprofiles.models import FriendRequest
from .factories import UserFactory, EventFactory


class TestEvent:
    def test_str(self):
        event = EventFactory(title='test_title')
        assert str(event) == 'test_title'

    def test_incr_views(self):
        event = EventFactory()
        event.incr_views()
        event.refresh_from_db()
        assert event.views == 1
        event.incr_views()
        event.refresh_from_db()
        assert event.views == 2

    def test_invited_by_status_no_invites(self):
        event = EventFactory()
        assert len(event.invited_by_status()) == 0

    def test_invited_by_status_with_invites(self):
        event = EventFactory()
        users = [UserFactory() for _ in range(4)]
        EventInvite.objects.join(event, users[0])  # self invite
        EventInvite.objects.invite(event, event.created_by, pk_or_pks=[user.pk for user in users[1:]])
        EventInvite.objects.accept(event.pk, users[1])
        EventInvite.objects.reject(event.pk, users[2])
        invited_by_status = event.invited_by_status()
        assert len(invited_by_status) == 4
        assert users[0] in invited_by_status.get('self')
        assert users[1] in invited_by_status.get('accepted')
        assert users[2] in invited_by_status.get('rejected')
        assert users[3] in invited_by_status.get('pending')

    def test_get_user_invite_when_no_invite(self):
        event = EventFactory()
        user = UserFactory()
        assert event._get_user_invite(user.pk) is None

    def test_get_user_invite_when_invite_exists(self):
        event = EventFactory()
        user = UserFactory()
        EventInvite.objects.invite(event, event.created_by, user.pk)
        assert event._get_user_invite(user.pk)

    class TestGetPermissionAndInvite:
        def test_public_event_no_invite(self):
            event = EventFactory()
            user = UserFactory()
            assert event.get_permission_and_invite(user) == (True, None)  # (is_permitted, invite)

        def test_public_event_with_invite(self):
            event = EventFactory()
            user = UserFactory()
            EventInvite.objects.invite(event, event.created_by, user.pk)
            invite = event._get_user_invite(user.pk)
            assert event.get_permission_and_invite(user) == (True, invite)

        def test_private_event_no_invite(self):
            event = EventFactory(privacy=Event.PRIVATE)
            user = UserFactory()
            assert event.get_permission_and_invite(user) == (False, None)

        def test_private_event_with_invite(self):
            event = EventFactory(privacy=Event.PRIVATE)
            user = UserFactory()
            EventInvite.objects.invite(event, event.created_by, user.pk)
            invite = event._get_user_invite(user.pk)
            assert event.get_permission_and_invite(user) == (True, invite)

        def test_private_event_no_invite_with_friendship(self):
            event = EventFactory(privacy=Event.PRIVATE)
            user = UserFactory()
            FriendRequest.objects.send_friend_request(user, event.created_by.pk)
            FriendRequest.objects.accept(event.created_by, user.pk)
            assert event.get_permission_and_invite(user) == (False, None)

        def test_friends_event_no_invite_no_friendship(self):
            event = EventFactory(privacy=Event.FRIENDS)
            user = UserFactory()
            assert event.get_permission_and_invite(user) == (False, None)

        def test_friends_event_with_invite(self):
            event = EventFactory(privacy=Event.FRIENDS)
            user = UserFactory()
            EventInvite.objects.invite(event, event.created_by, user.pk)
            invite = event._get_user_invite(user.pk)
            assert event.get_permission_and_invite(user) == (True, invite)

        def test_friends_event_no_invite_with_friendship(self):
            event = EventFactory(privacy=Event.FRIENDS)
            user = UserFactory()
            FriendRequest.objects.send_friend_request(user, event.created_by.pk)
            FriendRequest.objects.accept(event.created_by, user.pk)
            assert event.get_permission_and_invite(user) == (True, None)

        def test_friends_event_with_invite_with_friendship(self):
            event = EventFactory(privacy=Event.FRIENDS)
            user = UserFactory()
            EventInvite.objects.invite(event, event.created_by, user.pk)
            invite = event._get_user_invite(user.pk)
            FriendRequest.objects.send_friend_request(user, event.created_by.pk)
            FriendRequest.objects.accept(event.created_by, user.pk)
            assert event.get_permission_and_invite(user) == (True, invite)

    def test_self_invite_exists_with_self_invite(self):
        event = EventFactory()
        EventInvite.objects.join(event, event.created_by)
        assert event.self_invite_exists(event.created_by.pk)
        user = UserFactory()
        EventInvite.objects.join(event, user)
        assert event.self_invite_exists(user.pk)

    def test_self_invite_exists_no_self_invite(self):
        event = EventFactory()
        assert not event.self_invite_exists(event.created_by.pk)
        user = UserFactory()
        assert not event.self_invite_exists(user.pk)


class TestEventInvite:
    def test_str(self):
        event = EventFactory()
        user = UserFactory()
        EventInvite.objects.invite(event, event.created_by, user.pk)
        str_invite = str(event._get_user_invite(user.pk))
        result_expected = 'Event: {}; From: {}; To: {}; S: {}'.format(event.pk,
                                                                      event.created_by.pk,
                                                                      user.pk,
                                                                      EventInvite.PENDING)
        assert str_invite == result_expected

    def test_unique_together(self):
        event = EventFactory()
        user = UserFactory()
        invited_first = EventInvite.objects.invite(event, event.created_by, user.pk)
        invited_second = EventInvite.objects.invite(event, event.created_by, user.pk)
        assert invited_first and not invited_second
