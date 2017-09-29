from collections import defaultdict

from django.apps import apps
from django.db import models, IntegrityError
from django.db.models import Prefetch, Q, Count, Case, When, IntegerField
from django.utils import timezone

from common.cache import notify_by_cache


class EventManager(models.Manager):
    @property
    def EventInvite(self):
        return apps.get_model('events', 'EventInvite')

    def future_by_privacy(self, privacy=None, user=None):
        privacy_kw = {}
        if privacy:
            privacy_kw['privacy'] = privacy
        objs = self
        if user.is_authenticated:
            objs = self.with_user_invites(user)
        return objs.filter(
                **privacy_kw,
                start_date__gt=timezone.now()
            ).select_related('created_by').annotate(
            num_att=Count(Case(When(
                invites__status__in=(self.EventInvite.ACCEPTED, self.EventInvite.SELF), then=1
            ), output_field=IntegerField()))
        )

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

    def invited_and_attending(self, user):
        return self.future_by_privacy(user=user).filter(invites__to_user_id=user.pk)

    def search(self, privacy, user, search_str):
        return self.future_by_privacy(privacy, user).filter(
                (Q(title__icontains=search_str) | Q(description__icontains=search_str)))


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

    def remove(self, event, from_user, to_user_pk, *args):
        if event.created_by == from_user:
            return self.filter(event=event, to_user_id=to_user_pk).delete()
        return False

    def _single_invite(self, event, user, to_user_pk):
        if not event.created_by == user:
            return False
        try:
            obj, created = self.model.objects.get_or_create(event=event, from_user=user,
                                                            to_user_id=to_user_pk)
        except IntegrityError:
            return False
        else:
            if created:
                notify_by_cache('e_invites_count', to_user_pk)
                return True
            return False

    def _bulk_invite(self, event, user, to_user_pks):
        created = [self.model.objects._single_invite(event, user, pk) for pk in to_user_pks]

        if all(created):
            return True
        return False

    def invite(self, event, user, pk_or_pks):
        if isinstance(pk_or_pks, list):
            return self._bulk_invite(event, user, pk_or_pks)
        return self._single_invite(event, user, pk_or_pks)

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
