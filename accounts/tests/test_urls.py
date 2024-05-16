from django.contrib.auth import views as auth_views
from django.test import TestCase
from django.urls import resolve, reverse

from accounts import views


class UrlsTestCase(TestCase):
    """Test url patterns"""

    def test_profile_url(self):
        """Test profile url resolve"""

        url = reverse("accounts:profile")
        self.assertEqual(resolve(url).func.view_class, views.ProfileTemplateView)

    def test_profile_update_url(self):
        """Test profile update url resolve"""

        url = reverse("accounts:profile_update")
        self.assertEqual(resolve(url).func.view_class, views.ProfileUpdateView)

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

    def test_room_url(self):
        """Test room url resolve"""

        url = reverse("accounts:room")
        self.assertEqual(resolve(url).func.view_class, views.RoomTemplateView)

    # def test_room_join_url(self):
    #     """Test room_join url resolve"""

    #     url = reverse("accounts:room_join")
    #     self.assertEqual(resolve(url).func.view_class, views.RoomJoinView)

    def test_room_invitation_join_url(self):
        """Test room_invitation_join url resolve"""

        url = reverse("accounts:room_invitation_join")
        self.assertEqual(resolve(url).func.view_class, views.RoomInvitationJoinView)

    def test_room_invitation_accept_url(self):
        """Test room_invitation_accept url resolve"""

        url = reverse("accounts:room_invitation_accept")
        self.assertEqual(resolve(url).func.view_class, views.RoomInvitationAcceptView)

    def test_room_invitation_reject_url(self):
        """Test room_invitation_reject url resolve"""

        url = reverse("accounts:room_invitation_reject")
        self.assertEqual(resolve(url).func.view_class, views.RoomInvitationRejectView)

    def test_room_invitation_cancel_url(self):
        """Test room_invitation_cancel url resolve"""

        url = reverse("accounts:room_invitation_cancel")
        self.assertEqual(resolve(url).func.view_class, views.RoomInvitationCancelView)

    def test_room_create_url(self):
        """Test room_create url resolve"""

        url = reverse("accounts:room_create")
        self.assertEqual(resolve(url).func.view_class, views.RoomCreateView)

    def test_room_selection_url(self):
        """Test room_selection url resolve"""

        url = reverse("accounts:room_selection")
        self.assertEqual(resolve(url).func.view_class, views.RoomSelectionView)

    def test_room_invitation_url(self):
        """Test room_invitation url resolve"""

        url = reverse("accounts:room_invitation")
        self.assertEqual(resolve(url).func.view_class, views.RoomInvitationListView)

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
