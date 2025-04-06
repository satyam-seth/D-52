from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from records.validators import validate_past_datetime


class TestValidatePastDateTime(TestCase):
    """Test validate past datetime validator"""

    def test_valid_past_datetime(self):
        """test valid past datetime"""

        # Test with a datetime that is now
        now = timezone.now()
        self.assertIsNone(validate_past_datetime(now, days=6))

        # Test with a datetime that is within n days in the past
        past_date = now - timezone.timedelta(days=4)
        self.assertIsNone(validate_past_datetime(past_date, days=6))

    def test_future_datetime(self):
        """Test future datetime"""

        # Test with a future datetime
        future_datetime = timezone.now() + timezone.timedelta(days=1)

        with self.assertRaisesMessage(
            ValidationError,
            "The date and time cannot be in the future.",
        ):
            validate_past_datetime(future_datetime, days=6)

    def test_datetime_too_far_in_past(self):
        """Test datetime too far in fast"""

        # Test with a datetime that is more than n days in the past
        past_date = timezone.now() - timezone.timedelta(days=7)

        with self.assertRaisesMessage(
            ValidationError,
            "The date and time must be within the last 6 days.",
        ):
            validate_past_datetime(past_date, days=6)
