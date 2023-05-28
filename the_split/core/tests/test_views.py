from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from django.views.generic import TemplateView
from core.views import AboutTemplateView


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
