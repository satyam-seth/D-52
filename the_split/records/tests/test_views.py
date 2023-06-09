from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import Client, TestCase
from django.urls import reverse
from django.views.generic import TemplateView
from records.forms import RecordFrom, WaterFrom
from records.views import AddTemplateView

User = get_user_model()


class TestAddTemplateView(TestCase):
    """Test add template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            username="test-user", password="test-password"
        )
        self.url = reverse("records:add")

    def test_add_template_view_attributes(self) -> None:
        """Test add template view attributes"""

        view = AddTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertTrue(view.template_name, "records/add.html")

        context = view.get_context_data()

        # Assert that the values associated with the keys are of the expected types
        self.assertIsInstance(context["add_active"], str)
        self.assertIsInstance(context["record_form"], RecordFrom)
        self.assertIsInstance(context["water_form"], WaterFrom)

    def test_add_template_view_working(self) -> None:
        """Test add template view working"""

        # login user
        self.client.login(username="test-user", password="test-password")

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "records/add.html")

        # Assert context is correct
        self.assertEqual(response.context["add_active"], "active")
