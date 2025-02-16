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


# TODO: Remove it
def validate_past_date(value, n_days):
    """
    Validator function to ensure that the date is at least n days in the past
    and disallow future dates.
    """

    today = timezone.now().date()
    if value > today:
        raise ValidationError("Future dates are not allowed.")

    min_date = today - timezone.timedelta(days=6)
    if value < min_date:
        raise ValidationError(f"Date should be at least {n_days} days in the past.")


# TODO: Remove the hard-coded 6-day value and get it from a setting or environment variable
validate_past_date_within_past_6_days = partial(validate_past_date, n_days=6)

validate_past_datetime_within_past_6_days = partial(validate_past_datetime, days=6)
