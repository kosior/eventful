from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db.transaction import TransactionManagementError
from django.test import TestCase

from events.managers import EventManager
from events.models import EventInvite, Event
from .factories import EventFactory, UserFactory, FriendshipFactory


class TestEventManager:
    def test_event_invite_property(self):
        assert EventManager().EventInvite == EventInvite

    def test_future_by_privacy_without_kwargs_all_privacy(self):
        EventFactory(), EventFactory(privacy=Event.PRIVATE), EventFactory(privacy=Event.FRIENDS)
        events_fetched = Event.objects.future_by_privacy()
        assert len(events_fetched) == 3

    def test_future_by_privacy_without_user_only_public(self):
        EventFactory.create_batch(size=5)
        EventFactory.create_batch(size=2, privacy=Event.PRIVATE)
        EventFactory.create_batch(size=3, privacy=Event.FRIENDS)
        events_fetched = Event.objects.future_by_privacy(privacy=Event.PUBLIC)
        assert len(events_fetched) == 5

    def test_future_by_privacy_without_user_only_private(self):
        EventFactory.create_batch(size=2)
        EventFactory.create_batch(size=4, privacy=Event.PRIVATE)
        EventFactory.create_batch(size=1, privacy=Event.FRIENDS)
        events_fetched = Event.objects.future_by_privacy(privacy=Event.PRIVATE)
        assert len(events_fetched) == 4

    def test_future_by_privacy_without_user_only_friends(self):
        EventFactory.create_batch(size=1)
        EventFactory.create_batch(size=2, privacy=Event.PRIVATE)
        EventFactory.create_batch(size=6, privacy=Event.FRIENDS)
        events_fetched = Event.objects.future_by_privacy(privacy=Event.FRIENDS)
        assert len(events_fetched) == 6

    def test_future_by_privacy_with_user_not_authenticated(self):
        EventFactory()
        user = AnonymousUser()
        events_fetched = list(Event.objects.future_by_privacy(user=user))
        assert len(events_fetched) == 1
        assert hasattr(events_fetched[0], 'user_invite') is False

    def test_future_by_privacy_with_user_authenticated_self_invite(self):
        event = EventFactory(join=True)
        events_fetched = list(Event.objects.future_by_privacy(user=event.created_by))
        assert len(events_fetched) == 1
        assert events_fetched[0].user_invite[0].status == EventInvite.SELF

    def test_future_by_privacy_with_user_authenticated_pending_invite(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        events_fetched = list(Event.objects.future_by_privacy(user=user))
        assert len(events_fetched) == 1
        assert events_fetched[0].user_invite[0].status == EventInvite.PENDING

    def test_future_by_privacy_with_user_authenticated_accepted_invite(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        EventInvite.objects.accept(event.pk, user)
        events_fetched = list(Event.objects.future_by_privacy(user=user))
        assert len(events_fetched) == 1
        assert events_fetched[0].user_invite[0].status == EventInvite.ACCEPTED

    def test_future_by_privacy_with_user_authenticated_rejected_invite(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        EventInvite.objects.reject(event.pk, user)
        events_fetched = list(Event.objects.future_by_privacy(user=user))
        assert len(events_fetched) == 1
        assert events_fetched[0].user_invite[0].status == EventInvite.REJECTED

    def test_future_by_privacy_check_for_future_only_events(self):
        EventFactory.create_batch(size=5)
        EventFactory.create_batch(size=10, past_or_future='past')
        events_fetched = Event.objects.future_by_privacy()
        assert len(events_fetched) == 5

    def test_future_by_privacy_check_if_num_att_correct_without_accepted(self):
        event1 = EventFactory()
        event2 = EventFactory()
        UserFactory.create_batch(size=5, join_event=event1)
        UserFactory.create_batch(size=10, get_invited_to=event2)
        events = list(Event.objects.future_by_privacy())
        assert len(events) == 2
        assert events[0].num_att == 5
        assert events[1].num_att == 0

    def test_future_by_privacy_check_if_num_att_correct_with_pending_or_rejected(self):
        event1 = EventFactory()
        event2 = EventFactory()
        UserFactory.create_batch(size=5, get_invited_to=event1)
        users = UserFactory.create_batch(size=10, get_invited_to=event2)
        [EventInvite.objects.reject(event2.pk, user) for user in users]
        events = list(Event.objects.future_by_privacy())
        assert len(events) == 2
        assert events[0].num_att == 0
        assert events[1].num_att == 0

    def test_future_by_privacy_check_if_num_att_correct_with_accepted(self):
        event1 = EventFactory()
        event2 = EventFactory()
        UserFactory.create_batch(size=5, join_event=event1)
        users = UserFactory.create_batch(size=10, get_invited_to=event2)
        [EventInvite.objects.accept(event2.pk, user) for user in users[:8]]  # only 8 invitations accepted
        events = list(Event.objects.future_by_privacy())
        assert len(events) == 2
        assert events[0].num_att == 5
        assert events[1].num_att == 8

    def test_details(self, django_db_blocker):
        event = EventFactory(join=True)
        UserFactory.create_batch(size=5, get_invited_to=event)
        event_fetched = list(Event.objects.details().filter(pk=event.pk))[0]
        with django_db_blocker.block():
            assert event_fetched.created_by.username
            assert len(event_fetched.invites_list) == 6

    def test_friends_events_event_public_and_future(self):
        event = EventFactory()
        user = UserFactory(friend_user=event.created_by)
        events = list(Event.objects.friends_events(user))
        assert len(events) == 1
        assert event in events

    def test_friends_events_event_public_and_past(self):
        event = EventFactory(past_or_future='past')
        user = UserFactory(friend_user=event.created_by)
        events = list(Event.objects.friends_events(user))
        assert len(events) == 0

    def test_friends_events_event_friends(self):
        event = EventFactory(privacy=Event.FRIENDS)
        event2 = EventFactory(created_by=event.created_by, privacy=Event.FRIENDS)
        user = UserFactory(friend_user=event.created_by)
        events = list(Event.objects.friends_events(user))
        assert len(events) == 2
        assert event in events and event2 in events

    def test_friend_events_private_event_without_invitation(self):
        event = EventFactory(privacy=Event.PRIVATE)
        user = UserFactory(friend_user=event.created_by)
        events = list(Event.objects.friends_events(user))
        assert len(events) == 0

    def test_friend_events_private_event_with_invitation(self):
        event = EventFactory(privacy=Event.PRIVATE)
        user = UserFactory(friend_user=event.created_by)
        EventInvite.objects.invite(event, event.created_by, user.pk)
        events = list(Event.objects.friends_events(user))
        assert len(events) == 1

    def test_with_user_invites_without_invite(self):
        EventFactory.create_batch(size=3)
        user = UserFactory()
        events = Event.objects.with_user_invites(user).all()
        for event in events:
            assert len(event.user_invite) == 0

    def test_with_user_invites_with_invite(self):
        events = EventFactory.create_batch(size=4)
        user = UserFactory()
        EventInvite.objects.join(events[0], user)  # SELF
        EventInvite.objects.invite(events[1], events[1].created_by, user.pk)  # PENDING
        EventInvite.objects.invite(events[2], events[2].created_by, user.pk)  # ACCEPTED
        EventInvite.objects.invite(events[3], events[3].created_by, user.pk)  # REJECTED

        EventInvite.objects.accept(events[2].pk, user)
        EventInvite.objects.reject(events[3].pk, user)

        events_fetched = list(Event.objects.with_user_invites(user).all())
        assert events_fetched[0].user_invite[0].status == EventInvite.SELF
        assert events_fetched[1].user_invite[0].status == EventInvite.PENDING
        assert events_fetched[2].user_invite[0].status == EventInvite.ACCEPTED
        assert events_fetched[3].user_invite[0].status == EventInvite.REJECTED

    def test_invited_and_attending(self):
        event1 = EventFactory(privacy=Event.PRIVATE)
        event2 = EventFactory()
        event3 = EventFactory()
        user = UserFactory(get_invited_to=event1)
        EventInvite.objects.join(event2, user)
        events = Event.objects.invited_and_attending(user)
        assert len(events) == 2

    def test_search_title(self):
        EventFactory.create_batch(size=5)
        user = UserFactory()
        search_str = 'event'
        events = Event.objects.search(Event.PUBLIC, user, search_str)
        assert len(events) == 5

    def test_search_description(self):
        EventFactory(description='lorem ipsum test_desc .......')
        EventFactory(description='lorem ipsum test_d .......')
        EventFactory(description='lorem ipsum .......')
        user = UserFactory()
        search_str = 'test_desc'
        events = Event.objects.search(Event.PUBLIC, user, search_str)
        assert len(events) == 1

    def test_search_title_and_description(self):
        EventFactory(description='next example testing lorem ipsum')
        EventFactory(title='testing title 12345')
        EventFactory()
        user = UserFactory()
        search_str = 'testing'
        events = Event.objects.search(Event.PUBLIC, user, search_str)
        assert len(events) == 2

    def test_search_different_privacy(self):
        EventFactory(description='next example testing lorem ipsum')
        EventFactory(title='testing title 12345')
        EventFactory()
        user = UserFactory()
        search_str = 'testing'
        events1 = Event.objects.search(Event.PRIVATE, user, search_str)
        events2 = Event.objects.search(Event.FRIENDS, user, search_str)
        assert len(events1) == 0
        assert len(events2) == 0


class TestEventManagerQueriesNum(TestCase):
    def test_details(self):
        event = EventFactory()
        UserFactory(join_event=event)
        with self.assertNumQueries(2):
            event = list(Event.objects.details().filter(pk=event.pk))[0]
            [invite.to_user.username for invite in event.invites_list]


class TestEventInviteManager:
    def test_join_check_perm_false(self):
        events = [EventFactory(), EventFactory(privacy=Event.FRIENDS), EventFactory(privacy=Event.PRIVATE)]
        user = UserFactory()
        check_list = [EventInvite.objects.join(event, user, check_perm=False) for event in events]
        assert all(check_list)
        kw = {'from_user': user, 'to_user': user, 'status': EventInvite.SELF}
        invs_list = [EventInvite.objects.get(event=event, **kw) for event in events]
        assert all(invs_list)

    def test_join_check_perm_true(self):
        events = [EventFactory(), EventFactory(privacy=Event.FRIENDS), EventFactory(privacy=Event.PRIVATE)]
        user = UserFactory()
        check_list = [EventInvite.objects.join(event, user) for event in events]
        assert check_list == [True, False, False]

    def test_join_check_perm_true_user_is_creator(self):
        events = [EventFactory(), EventFactory(privacy=Event.FRIENDS), EventFactory(privacy=Event.PRIVATE)]
        check_list = [EventInvite.objects.join(event, event.created_by) for event in events]
        assert all(check_list)
        invs_list = [EventInvite.objects.get(
            event=event, from_user=event.created_by, to_user=event.created_by, status=EventInvite.SELF
        ) for event in events]
        assert all(invs_list)

    def test_join_chek_perm_true_friendship(self):
        event = EventFactory(privacy=Event.FRIENDS)
        user = UserFactory()
        FriendshipFactory(from_user=event.created_by, to_user=user)
        assert EventInvite.objects.join(event, user)

    def test_join_chek_perm_true_friendship_event_private(self):
        event = EventFactory(privacy=Event.PRIVATE)
        user = UserFactory()
        FriendshipFactory(from_user=event.created_by, to_user=user)
        assert not EventInvite.objects.join(event, user)

    def test_join_check_perm_true_users_already_invited(self):
        events = [EventFactory(), EventFactory(privacy=Event.FRIENDS), EventFactory(privacy=Event.PRIVATE)]
        users = [UserFactory(get_invited_to=event) for event in events]
        check_list = [EventInvite.objects.join(event, user, check_perm=True) for event, user in zip(events, users)]
        assert not any(check_list)

    def test_join_check_perm_false_user_already_invited(self):
        event = EventFactory(privacy=Event.PRIVATE)
        user = UserFactory(get_invited_to=event)
        assert not EventInvite.objects.join(event, user, check_perm=False)

    def test_join_check_perm_false_users_already_invited_transaction(self):
        event = EventFactory(privacy=Event.PRIVATE)
        user1 = UserFactory(get_invited_to=event)
        user2 = UserFactory(get_invited_to=event)
        with pytest.raises(TransactionManagementError):
            EventInvite.objects.join(event, user1, check_perm=False)
            EventInvite.objects.join(event, user2, check_perm=False)

    def test__update_status(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.PENDING
        EventInvite.objects._update_status(event_pk=event.pk, user=user, status=EventInvite.ACCEPTED)
        invite.refresh_from_db()
        assert invite.status == EventInvite.ACCEPTED

    def test_accept(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.PENDING
        EventInvite.objects.accept(event_pk=event.pk, user=user)
        invite.refresh_from_db()
        assert invite.status == EventInvite.ACCEPTED

    def test_reject(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.PENDING
        EventInvite.objects.reject(event_pk=event.pk, user=user)
        invite.refresh_from_db()
        assert invite.status == EventInvite.REJECTED

    def test_pend(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.PENDING
        EventInvite.objects.accept(event_pk=event.pk, user=user)
        invite.refresh_from_db()
        assert invite.status == EventInvite.ACCEPTED
        EventInvite.objects.pend(event_pk=event.pk, user=user)
        invite.refresh_from_db()
        assert invite.status == EventInvite.PENDING

    def test_self_remove(self):
        event = EventFactory()
        user = UserFactory(join_event=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.SELF
        EventInvite.objects.self_remove(event.pk, user)
        invites = list(EventInvite.objects.filter(event=event, to_user=user))
        assert len(invites) == 0

    def test_remove_requested_not_by_creator(self):
        event = EventFactory()
        user1 = UserFactory(join_event=event)
        user2 = UserFactory()
        invite = EventInvite.objects.get(event=event, to_user=user1)
        assert invite.status == EventInvite.SELF
        assert not EventInvite.objects.remove(event, user2, user1.pk)

    def test_remove_by_creator_self_invite(self):
        event = EventFactory()
        user = UserFactory(join_event=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.SELF
        deleted_count, _ = EventInvite.objects.remove(event, event.created_by, user.pk)
        assert deleted_count == 1

    def test_remove_by_creator_pending_invite(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        invite = EventInvite.objects.get(event=event, to_user=user)
        assert invite.status == EventInvite.PENDING
        deleted_count, _ = EventInvite.objects.remove(event, event.created_by, user.pk)
        assert deleted_count == 1

    def test__single_invite_user_not_creator(self):
        event = EventFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        assert not EventInvite.objects._single_invite(event, user1, user2.pk)

    @mock.patch('events.managers.notify_by_cache')
    def test__single_invite_user_is_creator(self, mocked_notify_by_cache):
        event = EventFactory()
        user = UserFactory()
        result = EventInvite.objects._single_invite(event, event.created_by, user.pk)
        mocked_notify_by_cache.assert_called_once_with('e_invites_count', user.pk)
        assert result
        invite = EventInvite.objects.get(event=event, from_user=event.created_by, to_user=user.pk)
        assert invite.status == EventInvite.PENDING

    def test__single_invite_invite_exists_intergity_error(self):
        event = EventFactory()
        user = UserFactory(join_event=event)
        assert not EventInvite.objects._single_invite(event, event.created_by, user.pk)

    def test__single_invite_invite_exists(self):
        event = EventFactory()
        user = UserFactory(get_invited_to=event)
        assert not EventInvite.objects._single_invite(event, event.created_by, user.pk)

    def test__bulk_invite(self):
        event = EventFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        assert EventInvite.objects._bulk_invite(event, event.created_by, [user1.pk, user2.pk])

    def test__bulk_invite_one_invite_exists(self):
        event = EventFactory()
        user1 = UserFactory(get_invited_to=event)
        user2 = UserFactory()
        assert not EventInvite.objects._bulk_invite(event, event.created_by, [user1.pk, user2.pk])

    def test_invite_pass_single_pk(self):
        event = EventFactory()
        user = UserFactory()
        assert EventInvite.objects.invite(event, event.created_by, user.pk)

    def test_invite_pass_list_of_pks(self):
        event = EventFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        assert EventInvite.objects.invite(event, event.created_by, [user1.pk, user2.pk])

    @mock.patch('events.managers.EventInviteManager._single_invite')
    def test_invite_patch_single_invite(self, mocked_single_invite):
        event = EventFactory()
        user = UserFactory()
        EventInvite.objects.invite(event, event.created_by, user.pk)
        mocked_single_invite.assert_called_once_with(event, event.created_by, user.pk)

    @mock.patch('events.managers.EventInviteManager._bulk_invite')
    def test_invite_patch_single_invite(self, mocked_bulk_invite):
        event = EventFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        EventInvite.objects.invite(event, event.created_by, [user1.pk, user2.pk])
        mocked_bulk_invite.assert_called_once_with(event, event.created_by, [user1.pk, user2.pk])

    def test_get_all_grouped(self):
        events = [
            EventFactory(),  # self invite
            EventFactory(privacy=Event.FRIENDS),  # accepted
            EventFactory(privacy=Event.PRIVATE),  # rejected
            EventFactory()  # pending
        ]
        user1 = UserFactory(join_event=events[0])
        user1_event = EventFactory(created_by=user1)
        user2 = UserFactory(get_invited_to=user1_event)
        [EventInvite.objects.invite(event, event.created_by, user1.pk) for event in events[1:]]
        EventInvite.objects.accept(events[1].pk, user1)
        EventInvite.objects.reject(events[2].pk, user1)
        user1_grouped_invites = EventInvite.objects.get_all_grouped(user1)
        assert len(user1_grouped_invites) == 5
        sent = user1_grouped_invites.get('sent')[0]
        self_ = user1_grouped_invites.get('self')[0]
        pen = user1_grouped_invites.get('pending')[0]
        acc = user1_grouped_invites.get('accepted')[0]
        rej = user1_grouped_invites.get('rejected')[0]
        assert sent.from_user == user1 and sent.to_user == user2 and sent.event == user1_event
        assert self_.event == events[0] and self_.status == EventInvite.SELF and self_.to_user == user1
        assert pen.event == events[3] and pen.status == EventInvite.PENDING and pen.to_user == user1
        assert acc.event == events[1] and acc.status == EventInvite.ACCEPTED and acc.to_user == user1
        assert rej.event == events[2] and rej.status == EventInvite.REJECTED and rej.to_user == user1
