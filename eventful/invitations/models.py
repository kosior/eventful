from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import IntegrityError

from events.models import Event


class Invitation(models.Model):
    ACCEPTED = 'A'
    REJECTED = 'R'
    PENDING = 'P'
    DUPLICATED = 'D'

    STATUS_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
        (DUPLICATED, 'Duplicated'),
    )

    from_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_sent')
    to_user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_received')
    status = models.CharField(choices=STATUS_CHOICES, max_length=1, default=PENDING)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.to_user_id} invited by {self.from_user_id}'


class EventInvitation(Invitation):
    event = models.ForeignKey(Event, related_name='invitations')

    class Meta:
        unique_together = ('to_user', 'event')


class FriendInvivationManager(models.Manager):
    def send_invitation(self, from_user_pk, to_user_pk):
        if from_user_pk == to_user_pk:
            raise ValidationError('from_user and to_user cannot be identical')

        try:
            obj, created = FriendInvitation.objects.get_or_create(from_user_id=from_user_pk, to_user_id=to_user_pk)
        except IntegrityError:
            return False
        else:
            if created:
                FriendInvitation.objects.get_or_create(from_user_id=to_user_pk, to_user_id=from_user_pk,
                                                       status=FriendInvitation.DUPLICATED)
                return True
            return False

    def get_invite_status(self, from_user, to_user):
        try:
            return FriendInvitation.objects.values_list('status', flat=True).get(from_user=from_user, to_user=to_user)
        except FriendInvitation.DoesNotExist:
            return

    def get_user_pending_invitations(self, user):
        invs = FriendInvitation.objects.filter(to_user=user, status=FriendInvitation.PENDING)
        return invs.select_related('from_user')

    def accept(self, from_user_pk, to_user_pk):
        users = (from_user_pk, to_user_pk)
        invs = FriendInvitation.objects.filter(from_user_id__in=users, to_user_id__in=users)
        if invs:
            for inv in invs.all():
                inv.status = FriendInvitation.ACCEPTED
                inv.save()
            return True
        return False

    def reject(self, from_user_pk, to_user_pk):
        users = (from_user_pk, to_user_pk)
        invs = FriendInvitation.objects.filter(from_user_id__in=users, to_user_id__in=users)
        for inv in invs.all():
            inv.delete()
        return True

    def get_friends(self, user):
        friends = FriendInvitation.objects.select_related('to_user')
        return friends.filter(from_user=user, status=FriendInvitation.ACCEPTED)


class FriendInvitation(Invitation):
    objects = FriendInvivationManager()

    class Meta:
        unique_together = ('from_user', 'to_user')
