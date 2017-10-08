from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile
from .utils import send_invites


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        pk = instance.pk
        UserProfile.objects.create(pk=pk, user=instance)
        send_invites(pk)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
