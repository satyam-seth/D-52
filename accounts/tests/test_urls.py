from accounts import views
from django.contrib.auth import views as auth_views
from django.test import TestCase
from django.urls import resolve, reverse


class UrlsTestCase(TestCase):
    """Test url patterns"""

    def test_login_url(self):
        """Test login url resolve"""

        url = reverse("accounts:login")
        self.assertEqual(resolve(url).func.view_class, views.UserLoginView)

    def test_logout_url(self):
        """Test logout url resolve"""

        url = reverse("accounts:logout")
        self.assertEqual(resolve(url).func.view_class, views.UserLogoutView)

    def test_signup_url(self):
        """Test signup url resolve"""

        url = reverse("accounts:signup")
        self.assertEqual(resolve(url).func.view_class, views.UserSignUpView)

    def test_group_url(self):
        """Test group url resolve"""

        url = reverse("accounts:group")
        self.assertEqual(resolve(url).func.view_class, views.GroupTemplateView)

    def test_group_join_url(self):
        """Test group_join url resolve"""

        url = reverse("accounts:group_join")
        self.assertEqual(resolve(url).func.view_class, views.GroupJoinView)

    def test_group_create_url(self):
        """Test group_create url resolve"""

        url = reverse("accounts:group_create")
        self.assertEqual(resolve(url).func.view_class, views.GroupCreateView)

    def test_password_reset_url(self):
        """Test password_reset url resolve"""

        url = reverse("accounts:password_reset")
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetView)

    def test_password_reset_done_url(self):
        """Test password_reset_done url resolve"""

        url = reverse("accounts:password_reset_done")
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetDoneView)

    def test_password_reset_confirm_url(self):
        """Test password_reset_confirm url resolve"""

        url = reverse(
            "accounts:password_reset_confirm", args=["uidb64", "token"]
        )  # Assuming uidb64 and token are provided
        self.assertEqual(
            resolve(url).func.view_class, auth_views.PasswordResetConfirmView
        )

    def test_password_reset_complete_url(self):
        """Test password_reset_complete url resolve"""

        url = reverse("accounts:password_reset_complete")
        self.assertEqual(
            resolve(url).func.view_class, views.MyPasswordResetCompleteView
        )
