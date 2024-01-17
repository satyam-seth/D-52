from django.test import TestCase

from core.forms import FeedbackFrom
from core.models import Feedback


class FeedbackFormTestCase(TestCase):
    """Test Feedback Form"""

    def test_feedback_form_fields(self) -> None:
        """Test feedback form fields"""

        form = FeedbackFrom()

        # assert meta class
        self.assertEqual(form.Meta.model, Feedback)
        self.assertEqual(form.Meta.fields, ["name", "problem", "message"])

        # assert name field
        self.assertEqual(
            form.Meta.widgets["name"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["name"].attrs["placeholder"],
            "Your full name",
        )

        # assert problem field
        self.assertEqual(
            form.Meta.widgets["problem"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["problem"].attrs["placeholder"],
            "Problem topic",
        )

        # assert message field
        self.assertEqual(
            form.Meta.widgets["message"].attrs["class"],
            "form-control",
        )
        self.assertEqual(
            form.Meta.widgets["message"].attrs["placeholder"],
            "Suggestion message",
        )
        self.assertEqual(
            form.Meta.widgets["message"].attrs["rows"],
            5,
        )

    def test_feedback_form_working(self):
        """Test feedback form working"""

        # initialize form data
        form_data = {
            "name": "test-name",
            "problem": "test-problem",
            "message": "test-message",
        }

        form = FeedbackFrom(data=form_data)

        # assert form is valid for valid form data
        self.assertTrue(form.is_valid())

        # assert form save create a group
        feedback = form.save()
        self.assertIsInstance(feedback, Feedback)
        self.assertEqual(feedback.name, form_data["name"])
        self.assertEqual(feedback.problem, form_data["problem"])
        self.assertEqual(feedback.message, form_data["message"])
