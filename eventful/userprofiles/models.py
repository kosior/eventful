from django.contrib.auth.models import User
from django.db import models

from .managers import FriendRequestManager


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=35, blank=True)
    friends = models.ManyToManyField('self')

    def __str__(self):
        return self.user.pk

    def are_friends(self, pk):
        return any(friend.pk == pk for friend in self.friends.all())


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent',
                                  on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received',
                                on_delete=models.CASCADE)
    objects = FriendRequestManager()

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user_id} sent request to {self.to_user_id}'
