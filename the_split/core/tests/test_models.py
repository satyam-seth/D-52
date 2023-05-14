from core.models import Feedback
from django.test import TestCase
from django.utils import timezone


class FeedBackModelTest(TestCase):
    """Test Feedback Model"""

    def test_feedback_creation(self) -> None:
        """Test feedback model instance creation is working"""

        # initialize data
        name = "test-user"
        problem = "test-problem"
        message = "test message"

        # create feedback instance
        feedback = Feedback.objects.create(name=name, problem=problem, message=message)

        # assert field values
        self.assertEqual(feedback.name, name)
        self.assertEqual(feedback.problem, problem)
        self.assertEqual(feedback.message, message)
        # TODO: fix this assertion
        # self.assertEqual(feedback.datetime, timezone.now())

        # assert string representation
        self.assertEqual(str(feedback), feedback.problem)
