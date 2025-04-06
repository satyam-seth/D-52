from datetime import datetime, timedelta
from functools import partial

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_past_datetime(value: datetime, days: int) -> None:
    """
    Validator function to ensure that the datetime is not in the future and is
    within the past 'n' number of days
    """

    now = timezone.now()
    n_days_ago = now - timedelta(days=days)

    # Check if the value is in the future
    if value > now:
        raise ValidationError("The date and time cannot be in the future.")

    # Check if the value is more than n days ago
    if value < n_days_ago:
        raise ValidationError(f"The date and time must be within the last {days} days.")


validate_past_datetime_within_past_6_days = partial(validate_past_datetime, days=6)
