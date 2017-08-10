from collections import defaultdict

from django.apps import apps
from django.db import models, IntegrityError
from django.db.models import Prefetch, Q
from django.utils import timezone


class EventManager(models.Manager):
    @property
    def EventInvite(self):
        return apps.get_model('events', 'EventInvite')

    def future_by_privacy(self, privacy, user):
        return self.with_user_invites(user).filter(
            privacy=privacy,
            start_date__gt=timezone.now()
        ).select_related('created_by')

    def details(self):
        prefetch_qs = self.EventInvite.objects.select_related('to_user')
        return self.model.objects.select_related('created_by').prefetch_related(
            Prefetch('invites', queryset=prefetch_qs)
        )

    def friends_events(self, user):
        friends_pks = user.profile.get_friends_pks()
        return self.with_user_invites(user).filter(
            created_by__in=friends_pks, start_date__gt=timezone.now()
        ).exclude(
            Q(privacy=self.model.PRIVATE) & ~Q(invites__to_user_id=user.pk)
        ).select_related('created_by')

    def with_user_invites(self, user):
        return self.prefetch_related(Prefetch(
                'invites',
                queryset=self.EventInvite.objects.filter(to_user=user),
                to_attr='user_invite'
            ))


class EventInviteManager(models.Manager):
    def join(self, event, user, *args, check_perm=True):
        perm, invite = (True, False) if not check_perm else event.get_permission_and_invite(user)
        if perm and not invite:
            try:
                self.create(event=event, from_user=user, to_user=user, status=self.model.SELF)
            except IntegrityError:
                return False
            else:
                return True
        return False

    def _update_status(self, event_pk, user, status):
        return self.filter(event_id=event_pk, to_user=user).update(status=status)

    def accept(self, event_pk, user, *args):
        return self._update_status(event_pk, user, self.model.ACCEPTED)

    def reject(self, event_pk, user, *args):
        return self._update_status(event_pk, user, self.model.REJECTED)

    def pend(self, event_pk, user, *args):
        return self._update_status(event_pk, user, self.model.PENDING)

    def self_remove(self, event_pk, user, *args):
        return self.filter(event_id=event_pk, from_user=user, status=self.model.SELF).delete()

    def remove(self, event_pk, from_user, to_user_pk, *args):
        return self.filter(event_id=event_pk, from_user=from_user, to_user_id=to_user_pk).delete()

    def invite(self, event, user, to_user_pk):
        if not event.created_by == user:
            return False
        try:
            obj, created = self.model.objects.get_or_create(event=event, from_user=user,
                                                            to_user_id=to_user_pk)
        except IntegrityError:
            return False
        else:
            if created:
                return True
            return False

    def get_all_grouped(self, user):
        invites = self.filter(Q(from_user=user) | Q(to_user=user))
        invites = invites.select_related('event', 'from_user', 'to_user')
        invites_grouped = defaultdict(list)
        for invite in invites:
            if invite.from_user == user and not invite.status == self.model.SELF:
                invites_grouped['sent'].append(invite)
            else:
                invites_grouped[invite.get_status_display()].append(invite)
        return invites_grouped
