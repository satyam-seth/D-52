from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import BaseCreatedModifiedModel, Feedback
from core.tests.mixin import AbstractModelMixinTestCase


class TestBaseCreatedModifiedModel(AbstractModelMixinTestCase):
    """Test Base created modified Model"""

    mixin = BaseCreatedModifiedModel

    def test_instance_creation(self) -> None:
        """Test creation of a model instance"""

        # Get current datetime
        now = timezone.now()

        # create model instance
        instance = self.model.objects.create()

        # Assert timestamps are close to the current time
        self.assertAlmostEqual(
            instance.created_on,
            now,
            delta=timedelta(milliseconds=500),
        )
        self.assertAlmostEqual(
            instance.modified_on,
            now,
            delta=timedelta(milliseconds=500),
        )


class TestFeedbackModel(TestCase):
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
