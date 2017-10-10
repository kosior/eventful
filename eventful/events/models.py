from collections import defaultdict

from django.contrib.auth.models import User
from django.db import models

from .managers import EventManager, EventInviteManager


class Event(models.Model):
    PUBLIC = 'PB'
    PRIVATE = 'PR'
    FRIENDS = 'FR'

    PRIVACY_CHOICES = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (FRIENDS, 'Friends only')
    )

    created_by = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=500, blank=True)
    start_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=2, choices=PRIVACY_CHOICES, default=PUBLIC)
    views = models.IntegerField(default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)

    objects = EventManager()

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title

    def incr_views(self):
        Event.objects.filter(pk=self.pk).update(views=models.F('views') + 1)

    def invited_by_status(self):
        invited_by_status = defaultdict(list)
        invites = self.invites.select_related('event', 'to_user')
        for invite in invites:
            invited_by_status[invite.get_status_display()].append(invite.to_user)
        return invited_by_status

    def _get_user_invite(self, user_pk):
        for invite in self.invites.all():
            if invite.to_user_id == user_pk:
                return invite

    def get_permission_and_invite(self, user):
        invite = self._get_user_invite(user.pk)
        if invite or self.privacy == self.PUBLIC or self.created_by_id == user.id:
            return True, invite
        elif self.privacy == self.FRIENDS and user.profile.are_friends_by_filter(self.created_by_id):
            return True, None
        return False, None

    def self_invite_exists(self, user_pk):
        return EventInvite.objects.filter(event=self, to_user_id=user_pk, status=EventInvite.SELF).exists()


class EventInvite(models.Model):
    ACCEPTED = 'A'
    REJECTED = 'R'
    PENDING = 'P'
    SELF = 'S'

    STATUS_CHOICES = (
        (ACCEPTED, 'accepted'),
        (REJECTED, 'rejected'),
        (PENDING, 'pending'),
        (SELF, 'self'),
    )

    event = models.ForeignKey(Event, related_name='invites', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='event_invites_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='event_invites_received', on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=1, default=PENDING)

    objects = EventInviteManager()

    class Meta:
        unique_together = ('event', 'to_user')

    def __str__(self):
        return 'Event: {}; From: {}; To: {}; S: {}'.format(self.event_id,
                                                           self.from_user_id,
                                                           self.to_user_id,
                                                           self.status)
