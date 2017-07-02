from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, editable=False)
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=35, blank=True)

    def __str__(self):
        return self.user.username
