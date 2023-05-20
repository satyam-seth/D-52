from http import HTTPStatus

from accounts.forms import LoginForm, SignUpForm
from accounts.views import (
    GroupTemplateView,
    UserLoginView,
    UserLogoutView,
    UserSignUpView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.test import Client, TestCase
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

User = get_user_model()


class TestUserLoginView(TestCase):
    """Test user login view"""

    def setUp(self) -> None:
        self.client = Client()

    def test_user_login_view_attributes(self):
        """Test user login view attributes"""

        view = UserLoginView()
        self.assertIsInstance(view, LoginView)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertEqual(view.authentication_form, LoginForm)
        self.assertEqual(view.template_name, "accounts/login.html")
        self.assertTrue(view.redirect_authenticated_user)
        self.assertEqual(view.success_message, "Logged In Successfully !!")
        self.assertEqual(view.extra_context, {"login_active": "active"})

    def test_user_login_view_rendering(self):
        """Test user login view rendering"""

        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "accounts/login.html")


class TestUserLogoutView(TestCase):
    """Test user logout view"""

    def setUp(self) -> None:
        self.client = Client()

    def test_user_logout_view_attributes(self):
        """Test user logout view attributes"""

        view = UserLogoutView()
        self.assertIsInstance(view, LogoutView)
        self.assertEqual(view.next_page, "core:home")
        self.assertEqual(view.success_message, "Logged Out Successfully !!")

    def test_user_logout_view_dispatch(self):
        """Test user logout view dispatch method"""

        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_logout_success_message(self):
        """Test user logout view redirecting properly and the message is present"""

        response = self.client.get(reverse("accounts:logout"), follow=True)
        self.assertRedirects(response, reverse("core:home"))
        self.assertContains(response, "Logged Out Successfully !!")


class TestUserSignUpView(TestCase):
    """Test user signup view"""

    def setUp(self) -> None:
        self.client = Client()

    def test_user_signup_view_attributes(self):
        """Test user signup view attributes"""

        view = UserSignUpView()
        self.assertIsInstance(view, CreateView)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertEqual(view.form_class, SignUpForm)
        self.assertEqual(view.template_name, "accounts/signup.html")
        self.assertTrue(view.success_url, reverse("accounts:group"))
        self.assertEqual(view.success_message, "Account Created Successfully !!")
        self.assertEqual(view.extra_context, {"signup_active": "active"})

    def test_signup_success(self):
        """Test user signup view working"""

        # Define the form data
        form_data = {
            "username": "test-user",
            "email": "testuser@example.com",
            "password1": "test-password",
            "password2": "test-password",
        }

        # Make a POST request to the signup view with the form data
        response = self.client.post(
            reverse("accounts:signup"),
            data=form_data,
            follow=True,
        )

        # Assert that the user is created and redirected to the specified URL
        self.assertRedirects(response, reverse("accounts:group"))

        # Assert that the user is created in the database
        self.assertTrue(User.objects.filter(username=form_data["username"]).exists())

        # Assert that the user is logged in
        self.assertTrue(
            self.client.login(
                username=form_data["username"],
                password=form_data["password1"],
            )
        )


class TestGroupTemplateView(TestCase):
    """Test user signup view working"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:group")

        # create test user
        self.user = User.objects.create_user(
            username="test-user", password="test-password"
        )
        # log in the user
        self.client.login(username="test-user", password="test-password")

    def test_group_template_view_attributes(self):
        """Test group template view attributes"""

        view = GroupTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.template_name, "accounts/group.html")

    def test_group_template_view_working(self):
        """Test group template view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "accounts/group.html")
