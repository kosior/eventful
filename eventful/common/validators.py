from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_start_date(value):
    if value < timezone.now() + timezone.timedelta(hours=1):
        raise ValidationError('Start date must be at least an hour from now.')
