from http import HTTPStatus
from unittest import mock, skip

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages import get_messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView

from accounts.forms import (
    LoginForm,
    ProfileUpdateForm,
    RoomCreateForm,
    RoomInvitationForm,
    SignUpForm,
)
from accounts.mixins import RoomAdminRequiredMixin, RoomInvitationTokenMixin
from accounts.models import Profile, Room, RoomInvitation, RoomMembership
from accounts.views import (
    ProfileTemplateView,
    ProfileUpdateView,
    RoomCreateView,
    RoomInvitationAcceptView,
    RoomInvitationCancelView,
    RoomInvitationJoinView,
    RoomInvitationListView,
    RoomInvitationRejectView,
    RoomInviteView,
    RoomSelectionView,
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
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
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
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
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


class TestRoomTemplateView(TestCase):
    """Test room template view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:room")

        # create test user
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
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
#             username="test-user",
#             password="test-password"
#             first_name="test",
#             last_name="user",
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
#         response_messages = tuple(get_messages(response.wsgi_request))
#         self.assertEqual(len(response_messages), 1)
#         self.assertEqual(response_messages[0].level, messages.SUCCESS)
#         self.assertEqual(
#             response_messages[0].message,
#             "You have joined the group test-group successfully !!",
#         )

#         # Assert that the user is redirected to the home page
#         self.assertRedirects(response, reverse("core:home"))


class TestRoomCerateView(TestCase):
    """Test room create view"""

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
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
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 2)
        self.assertEqual(response_messages[0].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[0].message,
            "Room 'test-room' created successfully!",
        )
        self.assertEqual(response_messages[1].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[1].message,
            "You have joined the room 'test-room' successfully !!",
        )

        # Assert that the user is redirected to the room invitation page
        self.assertRedirects(
            response,
            reverse("accounts:room_invitation"),
            fetch_redirect_response=False,
        )


class TestRoomInvitationListView(TransactionTestCase):
    """Test Room Invitation list view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("accounts:room_invitation")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

    def test_room_invitation_list_view_attributes(self) -> None:
        "Test Room Invitation list view attributes"

        view = RoomInvitationListView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomAdminRequiredMixin)
        self.assertIsInstance(view, ListView)
        self.assertEqual(view.model, RoomInvitation)
        self.assertEqual(view.paginate_by, 10)
        self.assertEqual(view.paginate_orphans, 5)
        self.assertEqual(view.ordering, ["-id"])
        self.assertEqual(view.context_object_name, "room_invitation_list")
        self.assertEqual(view.template_name, "accounts/room_invitation_list.html")
        self.assertEqual(view.extra_context, {"room_invitation_active": "active"})

    def test_room_invitation_list_view_working(self) -> None:
        """Test Room Invitation list view working"""

        # Create a room invitation
        RoomInvitation.objects.create(
            room=self.room,
            email="test@member.com",
            status=RoomInvitation.PENDING,
        )

        # login user
        self.client.login(email="test@user.com", password="test-password")

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

        # Make a GET request to the view
        response = self.client.get(self.url)

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that the template used is correct
        self.assertTemplateUsed(response, "accounts/room_invitation_list.html")

        # Check that the records are present in the context
        room_invitations = response.context["room_invitation_list"]
        self.assertQuerysetEqual(room_invitations, RoomInvitation.objects.all())

        # Check that room invitation form present in the context
        form = response.context["form"]
        self.assertIsInstance(form, RoomInvitationForm)


class TestRoomInviteView(TransactionTestCase):
    """Test Room Invite view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:room_invite")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

        # login user
        self.client.login(email="test@user.com", password="test-password")

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

    def test_room_invite_view_attributes(self) -> None:
        "Test Room Invite view attributes"

        view = RoomInviteView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomAdminRequiredMixin)
        self.assertIsInstance(view, View)

    @mock.patch("accounts.views.RoomInvitation.objects.send_invitation")
    def test_invite_new_member_form(self, mock_send_invitation):
        """Test invite new member"""

        # Post form
        data = {"email": "test@member.com"}
        response = self.client.post(self.url, data, follow=True)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[0].message,
            f"Email: '{data['email']}' is successfully invited to room '{self.room.name}'",
        )

        # Check if the view redirects to the room invitations page
        self.assertRedirects(response, reverse("accounts:room_invitation"))

        test_server_address = "http://testserver"
        invitation_url = reverse_lazy("accounts:room_invitation_join")
        absolute_invitation_url = test_server_address + invitation_url

        # Assert that the method was called with the correct parameters
        mock_send_invitation.assert_called_once_with(
            room=self.room,
            email=data["email"],
            absolute_invitation_url=absolute_invitation_url,
        )

    def test_invite_already_invited_member_form(self):
        """Test invite already invited member"""

        member_email = "test@member.com"

        # Create room invitation
        RoomInvitation.objects.create(room=self.room, email=member_email)

        # Post form
        data = {"email": member_email}
        response = self.client.post(self.url, data, follow=True)

        # Assert that the warning message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(
            response_messages[0].message,
            f"Email: '{member_email}' is already invited to room '{self.room.name}'",
        )

        # Check if the view redirects to the room invitations page
        self.assertRedirects(response, reverse("accounts:room_invitation"))

    def test_post_invalid_form(self):
        """Test post invalid form"""

        # Post empty form
        response = self.client.post(self.url, {}, follow=True)

        # Assert that the error message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.ERROR)
        self.assertEqual(response_messages[0].message, "Email: This field is required.")

        # Check if the view redirects to the room invitations page
        self.assertRedirects(response, reverse("accounts:room_invitation"))


class TestRoomSelectionView(TestCase):
    """Test Room Selection view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse_lazy("accounts:room_selection")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_room_invite_view_attributes(self) -> None:
        "Test Room Selection view attributes"

        view = RoomSelectionView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, View)

    def test_get_if_zero_room_memberships(self) -> None:
        """Test get if zero room membership"""

        # Get request
        response = self.client.get(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(
            response_messages[0].message,
            "Please create or join a room before selecting one.",
        )

        # Check if the view redirects to the room selection page
        self.assertRedirects(
            response, reverse_lazy("accounts:room"), fetch_redirect_response=False
        )

    def test_get_if_single_room_memberships_as_owner(self) -> None:
        """Test get if single room membership as owner"""

        # Create a room
        room = Room.objects.create(name="test-room", admin=self.user)

        # Get request
        response = self.client.get(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.INFO)
        self.assertEqual(
            response_messages[0].message,
            f"Welcome to the room '{room.name}'",
        )

        # Check room id set in session
        self.assertEqual(response.client.session["room_id"], room.id)

        # Check if the view redirects to the room invitation page
        self.assertRedirects(
            response,
            reverse_lazy("accounts:room_invitation"),
            fetch_redirect_response=False,
        )

    def test_get_if_single_room_memberships_as_member(self) -> None:
        """Test get if single room membership as member"""

        # Create member user
        member = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="member",
            last_name="user",
        )

        # Create a room
        room = Room.objects.create(name="test-room", admin=self.user)

        # Create membership
        RoomMembership.objects.create(member=member, room=room)

        # login user as member
        self.client.login(email="member@user.com", password="test-password")

        # Get request
        response = self.client.get(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        # self.assertEqual(response_messages[0].level, messages.INFO)
        self.assertEqual(
            response_messages[0].message,
            f"Welcome to the room '{room.name}'",
        )

        # Check room id set in session
        self.assertEqual(response.client.session["room_id"], room.id)

        # Check if the view redirects to the home page
        self.assertRedirects(
            response,
            reverse_lazy("core:home"),
            fetch_redirect_response=False,
        )

    def test_get_if_multiple_room_memberships(self) -> None:
        """Test get if multiple room membership"""

        # Create multiple rooms
        for i in range(16):
            Room.objects.create(name=f"test-room-{i}", admin=self.user)

        # Get request
        response = self.client.get(self.url)

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "accounts/room_selection.html")

        # Assert that only 10 room memberships are displayed on the page
        self.assertEqual(len(response.context["room_memberships_page"].object_list), 10)

        # Assert that pagination is working by checking the number of pages
        self.assertEqual(
            response.context["room_memberships_page"].paginator.num_pages, 2
        )

        # Check if the view displays the first page by default
        self.assertTrue(response.context["room_memberships_page"].has_next())
        self.assertFalse(response.context["room_memberships_page"].has_previous())

    def test_post_without_room_id(self) -> None:
        """Test post without room id data"""

        # Post empty form
        response = self.client.post(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(response_messages[0].message, "Room ID is required")

        # Check if the view redirects to the room selection page
        self.assertRedirects(response, self.url, fetch_redirect_response=False)

    def test_post_room_id_that_does_not_exist(self) -> None:
        """Test post room id that dose not exist"""

        # Post form
        response = self.client.post(self.url, {"roomId": 1})

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(response_messages[0].message, "Room does not exist")

        # Check if the view redirects to the room selection page
        self.assertRedirects(response, self.url, fetch_redirect_response=False)

    def test_post_room_id_user_not_member_of_the_room(self) -> None:
        """Test post room id user not member of the room"""

        # Create admin user
        admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="admin",
            last_name="user",
        )

        # Create a room
        room = Room.objects.create(name="test-room", admin=admin)

        # Post form
        response = self.client.post(self.url, {"roomId": room.id})

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.WARNING)
        self.assertEqual(
            response_messages[0].message,
            "You are not a member of requested Room",
        )

        # Check if the view redirects to the room selection page
        self.assertRedirects(response, self.url, fetch_redirect_response=False)

    def test_post_room_id_user_member_of_the_room(self) -> None:
        """Test post room id user not member of the room"""

        # Create a room
        room = Room.objects.create(name="test-room", admin=self.user)

        # Post form
        response = self.client.post(self.url, {"roomId": room.id})

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.INFO)
        self.assertEqual(
            response_messages[0].message,
            f"Welcome to the room '{room.name}'",
        )

        # Check room id set in session
        self.assertEqual(response.client.session["room_id"], room.id)

        # Check if the view redirects to the room selection page
        self.assertRedirects(
            response,
            reverse_lazy("core:home"),
            fetch_redirect_response=False,
        )


class TestRoomInvitationJoinView(TestCase):
    """Test Room Invitation Join view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse_lazy("accounts:room_invitation_join")
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # login user
        self.client.login(email="test@user.com", password="test-password")

    def test_room_invitation_join_view_attributes(self) -> None:
        "Test Room Invitation Join view attributes"

        view = RoomInvitationJoinView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomInvitationTokenMixin)
        self.assertIsInstance(view, View)

    @mock.patch("accounts.views.RoomInvitationJoinView.get_token")
    def test_returns_response_if_get_token_returns_http_response(
        self, mock_get_token
    ) -> None:
        """Test returns response if get token returns http response"""

        # Set return value
        mock_response = HttpResponse("Test Response")
        mock_get_token.return_value = mock_response

        # Send GET request to the view
        response = self.client.get(self.url)

        # Assert response
        self.assertEqual(response, mock_response)

        # Assert get_token called once with expected request
        mock_get_token.assert_called_once_with(response.wsgi_request)

    @mock.patch("accounts.views.RoomInvitationJoinView.get_token")
    def test_render_template_if_get_token_returns_token(self, mock_get_token) -> None:
        """Test render template if get token returns token"""

        # Set return value
        test_token = "test_token"
        mock_get_token.return_value = test_token

        # Send a POST request to the view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert that the correct template is used
        self.assertTemplateUsed(response, "accounts/room_invitation_join.html")

        # Assert response context token
        self.assertEqual(response.context["token"], test_token)

        # Assert get_token called once with expected request
        mock_get_token.assert_called_once_with(response.wsgi_request)


class TestRoomInvitationAcceptView(TestCase):
    """Test Room Invitation Accept view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse_lazy("accounts:room_invitation_accept")
        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="test",
            last_name="admin",
        )
        self.member = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="test",
            last_name="member",
        )
        self.room = Room.objects.create(name="test-room", admin=self.admin)

        # login user
        self.client.login(email="member@user.com", password="test-password")

    def test_room_invitation_accept_view_attributes(self) -> None:
        "Test Room Invitation accept view attributes"

        view = RoomInvitationAcceptView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomInvitationTokenMixin)
        self.assertIsInstance(view, View)

    @mock.patch("accounts.views.RoomInvitationAcceptView.get_token")
    def test_returns_response_if_get_token_returns_http_response(
        self, mock_get_token
    ) -> None:
        """Test returns response if get token returns http response"""

        # Set return value
        mock_response = HttpResponse("Test Response")
        mock_get_token.return_value = mock_response

        # Send POST request to the view
        response = self.client.post(self.url)

        # Assert response
        self.assertEqual(response, mock_response)

    @mock.patch("accounts.views.RoomInvitation.objects.unsigned_token")
    @mock.patch("accounts.views.RoomInvitation.objects.accept_invitation")
    @mock.patch("accounts.views.RoomInvitationAcceptView.get_token")
    def test_accept_invitation_if_token_valid(
        self,
        mock_get_token,
        mock_accept_invitation,
        mock_unsigned_token,
    ) -> None:
        """Test accept invitation if token valid"""

        # Set return value
        test_token = "test_token"
        test_token_payload = {"id": 1, "room": self.room.pk, "email": self.member.email}
        mock_get_token.return_value = test_token
        mock_accept_invitation.return_value = None
        mock_unsigned_token.return_value = test_token_payload

        # Send a POST request to the view
        response = self.client.post(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.SUCCESS)
        self.assertEqual(
            response_messages[0].message,
            f"Room '{self.room.name}' invitation accepted successfully.",
        )

        # Assert that the user is redirected to the room selection page
        self.assertRedirects(
            response,
            reverse("accounts:room_selection"),
            fetch_redirect_response=False,
        )

        # Assert get_token called once with expected request
        mock_get_token.assert_called_once_with(response.wsgi_request)

        # Assert accept_invitation called once with expected args
        mock_accept_invitation.assert_called_once_with(
            current_user=self.member,
            token=test_token,
        )

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(test_token)


class TestRoomInvitationRejectView(TestCase):
    """Test Room Invitation Reject view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse_lazy("accounts:room_invitation_reject")
        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="test",
            last_name="admin",
        )
        self.member = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="test",
            last_name="member",
        )
        self.room = Room.objects.create(name="test-room", admin=self.admin)

        # login user
        self.client.login(email="member@user.com", password="test-password")

    def test_room_invitation_reject_view_attributes(self) -> None:
        "Test Room Invitation reject view attributes"

        view = RoomInvitationRejectView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomInvitationTokenMixin)
        self.assertIsInstance(view, View)

    @mock.patch("accounts.views.RoomInvitationRejectView.get_token")
    def test_returns_response_if_get_token_returns_http_response(
        self, mock_get_token
    ) -> None:
        """Test returns response if get token returns http response"""

        # Set return value
        mock_response = HttpResponse("Test Response")
        mock_get_token.return_value = mock_response

        # Send POST request to the view
        response = self.client.post(self.url)

        # Assert response
        self.assertEqual(response, mock_response)

    @mock.patch("accounts.views.RoomInvitation.objects.unsigned_token")
    @mock.patch("accounts.views.RoomInvitation.objects.reject_invitation")
    @mock.patch("accounts.views.RoomInvitationRejectView.get_token")
    def test_reject_invitation_if_token_valid(
        self,
        mock_get_token,
        mock_reject_invitation,
        mock_unsigned_token,
    ) -> None:
        """Test reject invitation if token valid"""

        # Set return value
        test_token = "test_token"
        test_token_payload = {"id": 1, "room": self.room.pk, "email": self.member.email}
        mock_get_token.return_value = test_token
        mock_reject_invitation.return_value = None
        mock_unsigned_token.return_value = test_token_payload

        # Send a POST request to the view
        response = self.client.post(self.url)

        # Assert that the success message is displayed
        response_messages = tuple(get_messages(response.wsgi_request))
        self.assertEqual(len(response_messages), 1)
        self.assertEqual(response_messages[0].level, messages.INFO)
        self.assertEqual(
            response_messages[0].message,
            f"Room '{self.room.name}' invitation rejected successfully.",
        )

        # Assert that the user is redirected to the home page
        self.assertRedirects(
            response,
            reverse("core:home"),
            fetch_redirect_response=False,
        )

        # Assert get_token called once with expected request
        mock_get_token.assert_called_once_with(response.wsgi_request)

        # Assert accept_invitation called once with expected args
        mock_reject_invitation.assert_called_once_with(
            current_user=self.member,
            token=test_token,
        )

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(test_token)


class TestRoomInvitationCancelView(TestCase):
    """Test Room Invitation Cancel view"""

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse_lazy("accounts:room_invitation_cancel")
        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="test",
            last_name="admin",
        )
        self.room = Room.objects.create(name="test-room", admin=self.admin)
        self.invitation = RoomInvitation.objects.create(
            room=self.room, email="member@user.com"
        )

        # login user
        self.client.login(email="admin@user.com", password="test-password")

        # Set room id in session
        session = self.client.session
        session["room_id"] = self.room.id
        session.save()

    def test_room_invitation_cancel_view_attributes(self) -> None:
        "Test Room Invitation cancel view attributes"

        view = RoomInvitationCancelView()
        self.assertIsInstance(view, LoginRequiredMixin)
        self.assertIsInstance(view, RoomAdminRequiredMixin)
        self.assertIsInstance(view, View)

    def test_returns_404_not_found_if_invitation_id_missing(self) -> None:
        """Test returns 404 not found if invitation id missing"""

        # Send a POST request to the view
        response = self.client.post(self.url)

        # Assert response is 404 not found
        self.assertIsInstance(response, HttpResponseNotFound)

    @mock.patch("accounts.views.RoomInvitation.cancel")
    def test_returns_400_bad_request_if_validation_error_is_raised_on_invitation_cancel(
        self,
        mock_cancel,
    ) -> None:
        """Test returns 400 bad request if validation error is raised on invitation cancel"""

        # Raise value error
        mock_cancel.side_effect = ValidationError("test-error-message")

        # Send a POST request to the view
        response = self.client.post(
            self.url, data={"invitation_id": self.invitation.id}
        )

        # Assert response is 400 bad request
        self.assertIsInstance(response, HttpResponseBadRequest)

        # Assert invitation cancel called
        mock_cancel.assert_called_once()
