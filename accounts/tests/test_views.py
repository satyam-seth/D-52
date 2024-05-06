from http import HTTPStatus
from unittest import skip

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages import get_messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.views.generic import CreateView, FormView, TemplateView

from accounts.forms import LoginForm, ProfileUpdateForm, RoomCreateForm, SignUpForm
from accounts.models import Profile
from accounts.views import (
    ProfileTemplateView,
    ProfileUpdateView,
    RoomCreateView,
    RoomTemplateView,
    UserLoginView,
    UserLogoutView,
    UserSignUpView,
)

User = get_user_model()


class TestProfileTemplateView(TestCase):
    """Test Profile template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:profile")

        # create test user
        self.user = User.objects.create_user(
            email="test@user.com", password="test-password"
        )
        # log in the user
        self.client.login(email="test@user.com", password="test-password")

    def test_profile_template_view_attributes(self):
        """Test profile template view attributes"""

        view = ProfileTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.template_name, "accounts/profile.html")

    def test_profile_template_view_working(self):
        """Test profile template view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "accounts/profile.html")


class TestProfileUpdateView(TestCase):
    """Test profile update view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:profile_update")

        # create test user
        self.user = User.objects.create_user(
            email="test@user.com", password="test-password"
        )
        # log in the user
        self.client.login(email="test@user.com", password="test-password")

    def test_profile_update_view_attributes(self):
        """Test profile update view attributes"""

        view = ProfileUpdateView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertIsInstance(view, FormView)
        self.assertEqual(view.form_class, ProfileUpdateForm)
        self.assertEqual(view.template_name, "accounts/profile_update.html")
        self.assertTrue(view.success_url, reverse("accounts:profile"))
        self.assertEqual(view.success_message, "Profile Updated !!")

    # Upload a valid image. The file you uploaded was either not an image or a corrupted image.
    @skip("Debug why form_valid method not run")
    def test_profile_update_view_working(self):
        """Test profile update view working"""

        avatar = SimpleUploadedFile(
            name="test_avatar.jpg",
            content=b"file_content",
            content_type="image/jpeg",
        )
        cover_photo = SimpleUploadedFile(
            name="test_cover_photo.jpg",
            content=b"file_content",
            content_type="image/jpeg",
        )

        # Prepare the form data
        form_data = {"avatar": avatar, "cover_photo": cover_photo}

        # Use the client's form property to submit the data
        response = self.client.post(self.url, form_data, follow=True)

        # Check if the view redirects to the success URL
        self.assertRedirects(response, reverse("accounts:profile"))

        # Check if the profile has been updated with the correct data
        updated_profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile.avatar.name, f"profile_avatars/{avatar.name}")
        self.assertEqual(
            updated_profile.cover_photo.name, f"profile_cover_photos/{cover_photo.name}"
        )


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
        self.url = reverse("accounts:signup")

    def test_user_signup_view_attributes(self):
        """Test user signup view attributes"""

        view = UserSignUpView()
        self.assertIsInstance(view, CreateView)
        self.assertIsInstance(view, SuccessMessageMixin)
        self.assertEqual(view.form_class, SignUpForm)
        self.assertEqual(view.template_name, "accounts/signup.html")
        self.assertTrue(view.success_url, reverse("accounts:room"))
        self.assertEqual(view.success_message, "Account Created Successfully !!")
        self.assertEqual(view.extra_context, {"signup_active": "active"})

    def test_signup_success(self):
        """Test user signup view working"""

        # Define the form data
        form_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "test-password",
            "password2": "test-password",
        }

        # Make a POST request to the signup view with the form data
        response = self.client.post(
            self.url,
            data=form_data,
            follow=True,
        )

        # Assert that the user is created and redirected to the specified URL
        self.assertRedirects(response, reverse("accounts:room"))

        # Assert that the user is created in the database
        self.assertTrue(User.objects.filter(email=form_data["email"]).exists())

        # Assert that the user is logged in
        self.assertTrue(
            self.client.login(
                username=form_data["email"],
                password=form_data["password1"],
            )
        )


class TestRoomTemplateView(TestCase):
    """Test room template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:room")

        # create test user
        self.user = User.objects.create_user(
            email="test@user.com", password="test-password"
        )
        # log in the user
        self.client.login(email="test@user.com", password="test-password")

    def test_room_template_view_attributes(self):
        """Test room template view attributes"""

        view = RoomTemplateView()
        self.assertIsInstance(view, TemplateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.template_name, "accounts/room.html")

    def test_room_template_view_working(self):
        """Test room template view working"""

        # Send a GET request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "accounts/room.html")


# class TestGroupJoinView(TestCase):
#     """Test group join view"""

#     def setUp(self) -> None:
#         self.client = Client()
#         self.url = reverse("accounts:group_join")
#         self.user = User.objects.create_user(
#             username="test-user", password="test-password"
#         )
#         self.group = Group.objects.create(name="test-group")

#     def test_group_join_view_attributes(self):
#         """Test group join view attributes"""

#         view = RoomJoinView()
#         self.assertIsInstance(view, FormView)
#         self.assertIsInstance(view, LoginRequiredMixin)
#         self.assertEqual(view.form_class, RoomJoinForm)
#         self.assertEqual(view.template_name, "accounts/group_join.html")
#         self.assertTrue(view.success_url, reverse("core:home"))

#     def test_group_join_view_working(self) -> None:
#         """Test group join view working"""

#         # Log in the user
#         self.client.login(username="test-user", password="test-password")

#         # Send a POST request to the view with the group name
#         response = self.client.post(self.url, {"group_name": "test-group"})

#         # Assert that the response status code is 302 (redirect)
#         self.assertEqual(response.status_code, HTTPStatus.FOUND)

#         # Assert that the user is added to the group
#         self.assertIn(self.group, self.user.groups.all())

#         # Assert that the success message is displayed
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertEqual(
#             str(messages[0]),
#             "You have joined the group test-group successfully !!",
#         )

#         # Assert that the user is redirected to the home page
#         self.assertRedirects(response, reverse("core:home"))


class TestRoomCerateView(TestCase):
    """Test room create view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@user.com", password="test-password"
        )
        self.url = reverse("accounts:room_create")

    def test_room_create_view_attributes(self):
        """Test room create view attributes"""

        view = RoomCreateView()
        self.assertIsInstance(view, CreateView)
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertEqual(view.form_class, RoomCreateForm)
        self.assertEqual(view.template_name, "accounts/room_create.html")
        self.assertEqual(view.success_url, reverse("accounts:room_invitation"))

    def test_room_create_view_working(self) -> None:
        """Test room create view working"""

        # Log in the user
        self.client.login(email="test@user.com", password="test-password")

        # Send a POST request to the view with the room name
        response = self.client.post(self.url, data={"name": "test-room"})

        # Assert that the response status code is 302 (redirect)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        # Assert that the success message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(
            str(messages[0]),
            "Room 'test-room' created successfully!",
        )
        self.assertEqual(
            str(messages[1]),
            "You have joined the room 'test-room' successfully !!",
        )

        # Assert that the user is redirected to the room invitation page
        self.assertRedirects(
            response,
            reverse("accounts:room_invitation"),
            fetch_redirect_response=False,
        )


class TestMyPasswordResetCompleteView(TestCase):
    """Test my password reset complete view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:password_reset_complete")

    def test_my_password_reset_complete_view_working(self):
        """Test my password reset complete view working"""

        # Send a GET request to the password reset complete URL
        response = self.client.get(self.url)

        # Verify that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Verify that the correct template is used
        self.assertTemplateUsed(response, "registration/password_reset_complete.html")

        # Verify that the 'login_url' variable is included in the context and has the correct value
        self.assertEqual(response.context["login_url"], "/login/")
