from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from records.validators import validate_past_date


class TestValidatePastDate(TestCase):
    """Test validate past date validator"""

    def test_valid_past_date(self):
        """test valid past date"""

        # Test with a date that is today
        today = timezone.now().date()
        self.assertIsNone(validate_past_date(today, n_days=6))

        # Test with a date that is within 6 days in the past
        past_date = today - timezone.timedelta(days=6)
        self.assertIsNone(validate_past_date(past_date, n_days=6))

    def test_future_date(self):
        """Test future date"""

        # Test with a future date
        future_date = timezone.now().date() + timezone.timedelta(days=1)

        with self.assertRaisesMessage(
            ValidationError,
            "Future dates are not allowed.",
        ):
            validate_past_date(future_date, n_days=6)

    def test_date_too_far_in_past(self):
        """Test date too far in fast"""

        # Test with a date that is more than 6 days in the past
        today = timezone.now().date()
        past_date = today - timezone.timedelta(days=7)

        with self.assertRaisesMessage(
            ValidationError,
            "Date should be at least 6 days in the past.",
        ):
            validate_past_date(past_date, n_days=6)
