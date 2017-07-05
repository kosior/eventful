from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

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
    def send_invitation(self, from_user, to_user):
        if from_user == to_user:
            raise ValidationError('from_user and to_user cannot be identical')

        obj, created = FriendInvitation.objects.get_or_create(from_user=from_user, to_user=to_user)

        if created:
            FriendInvitation.objects.get_or_create(from_user=to_user, to_user=from_user,
                                                   status=FriendInvitation.DUPLICATED)
            return True
        return False


class FriendInvitation(Invitation):
    objects = FriendInvivationManager()

    class Meta:
        unique_together = ('from_user', 'to_user')
