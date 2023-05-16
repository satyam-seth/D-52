from http import HTTPStatus

from accounts.forms import LoginForm
from accounts.views import UserLoginView
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.test import Client, TestCase
from django.urls import reverse


class TestUserLoginView(TestCase):
    """Test user login view"""

    def setUp(self):
        self.client = Client()

    def test_user_login_view_attributes(self):
        """test user login view attributes"""

        view = UserLoginView()
        self.assertIsInstance(view, LoginView)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertEqual(view.authentication_form, LoginForm)
        self.assertEqual(view.template_name, "accounts/login.html")
        self.assertTrue(view.redirect_authenticated_user)
        self.assertEqual(view.success_message, "Logged In Successfully !!")
        self.assertEqual(view.extra_context, {"login_active": "active"})

    def test_user_login_view_rendering(self):
        """test user login view rendering"""

        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "accounts/login.html")
