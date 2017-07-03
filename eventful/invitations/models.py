from django.contrib.auth.models import User
from django.db import models

from events.models import Event


class Invitation(models.Model):
    ACCEPTED = 'A'
    REJECTED = 'R'
    PENDING = 'P'

    STATUS_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending')
    )

    inviter = models.ForeignKey(User, related_name='%(class)s_sent')
    to_user = models.ForeignKey(User, related_name='%(class)s_received')
    status = models.CharField(choices=STATUS_CHOICES, max_length=1, default=PENDING)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.to_user.username} invited by {self.inviter.username}'


class EventInvitation(Invitation):
    event = models.ForeignKey(Event, related_name='invitations')

    class Meta:
        unique_together = (('to_user', 'event'),)


class FriendInvitation(Invitation):
    class Meta:
        unique_together = (('inviter', 'to_user'),)
