from http import HTTPStatus

from core.forms import FeedbackFrom
from core.views import AboutTemplateView, FeedbackCreateView
from django.contrib.messages import get_messages
from django.contrib.messages.views import SuccessMessageMixin
from django.test import Client, TestCase
from django.urls import reverse
from django.views.generic import CreateView, TemplateView


class TestAboutTemplateView(TestCase):
    "Test about template view"

    def setUp(self):
        self.client = Client()
        self.url = reverse("core:about")
        self.context = {"about_active": "active"}

    def test_about_template_view_attributes(self):
        """Test about template view attributes"""

        view = AboutTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertEqual(view.template_name, "core/about.html")
        self.assertEqual(view.extra_context, self.context)

    def test_group_template_view_working(self):
        """Test group template view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "core/about.html")

        # Assert context is correct
        self.assertEqual(response.context["about_active"], self.context["about_active"])


class TestFeedbackCerateView(TestCase):
    """Test feedback create view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("core:feedback")
        self.success_message = "Thank you for your valuable feedback, it will help us to improve your experience."

    def test_feedback_create_view_attributes(self):
        """Test feedback create view attributes"""

        view = FeedbackCreateView()
        self.assertIsInstance(view, CreateView)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertEqual(view.form_class, FeedbackFrom)
        self.assertEqual(view.template_name, "core/feedback.html")
        self.assertTrue(view.success_url, reverse("core:home"))
        self.assertTrue(view.success_message, self.success_message)

    def test_feedback_create_view_working(self) -> None:
        """Test feedback create view working"""

        # Send a POST request to the view with the feedback data
        response = self.client.post(
            self.url,
            data={
                "name": "test-name",
                "problem": "test-problem",
                "message": "test-message",
            },
        )

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert that the success message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), self.success_message)

        # Assert that the user is redirected to the home page
        self.assertRedirects(response, reverse("core:home"))
