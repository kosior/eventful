from django.db import models


class Event(models.Model):
    PUBLIC = 'PB'
    PRIVATE = 'PR'
    FRIENDS = 'FR'

    PRIVACY_CHOICES = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (FRIENDS, 'Friends only')
    )

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=500, blank=True)
    start_date = models.DateTimeField()
    creation_date = models.DateTimeField(auto_now_add=True)
    privacy = models.CharField(max_length=2, choices=PRIVACY_CHOICES, default=PUBLIC)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title
