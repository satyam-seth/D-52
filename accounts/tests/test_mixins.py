from http import HTTPStatus
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.base import SessionBase
from django.core.signing import BadSignature
from django.http import Http404, HttpResponseBadRequest, HttpResponseNotFound
from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy

from accounts.mixins import (
    RoomAdminRequiredMixin,
    RoomBaseMixin,
    RoomInvitationTokenMixin,
    RoomRequiredMixin,
)
from accounts.models import Room, RoomInvitation

User = get_user_model()


class TestRoomBaseMixin(TestCase):
    """Test Room Base Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = SessionBase()
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.request.user = self.user

        # Create a view instance with the RoomBaseMixin
        self.view = RoomBaseMixin()

    def test_get_room_id(self) -> None:
        """Test get room id"""

        self.assertIsNone(self.view.get_room_id(self.request))

        # Set room id in session
        self.request.session["room_id"] = 1

        self.assertEqual(self.view.get_room_id(self.request), 1)

    def test_handle_on_room(self) -> None:
        """Test handle no room"""

        # Call the dispatch method with the request
        response = self.view.dispatch(self.request)

        # Check that the response is a redirect to the room selection page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse_lazy("accounts:room_selection"))

    def test_handle_room_exists(self) -> None:
        """Test handle no room exits"""

        # Set room id in session
        self.request.session["room_id"] = 1

        # Assert calling dispatch should call super dispatch
        with self.assertRaisesMessage(
            AttributeError, "'super' object has no attribute 'dispatch'"
        ):
            # Call the dispatch method with the request
            self.view.dispatch(self.request)

    def test_get_room_working_if_room_found(self) -> None:
        """Test get_room working if room found"""

        # create room
        room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        self.request.session["room_id"] = room.id

        self.assertEqual(self.view.get_room(self.request), room)

    def test_get_room_working_if_room_not_found(self) -> None:
        """Test get_room working if room not found"""

        # Set invalid room id in session
        self.request.session["room_id"] = 9999

        # Assert calling get_room should raises Http404 exception
        with self.assertRaisesMessage(Http404, "No Room matches the given query."):
            # Call the get_room method with the request
            self.view.get_room(self.request)


class TestRoomRequiredMixin(TestCase):
    """Test Room Required Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = SessionBase()

        # create user
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # set current user
        self.request.user = self.user

        # Create a view instance with the RoomRequiredMixin
        self.view = RoomRequiredMixin()

    def test_redirect_to_room_selection(self) -> None:
        """Test redirect to room selection"""

        # Call the dispatch method with the request
        response = self.view.dispatch(self.request)

        # Check that the response is a redirect to the room selection page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse_lazy("accounts:room_selection"))

    def test_not_redirect_to_room_selection(self) -> None:
        """Test not redirect to room selection"""

        # create room
        room = Room.objects.create(name="test-room", admin=self.user)

        # Set room id in session
        self.request.session["room_id"] = room.id

        # Assert calling dispatch should call super dispatch
        with self.assertRaisesMessage(
            AttributeError, "'super' object has no attribute 'dispatch'"
        ):
            # Call the dispatch method with the request
            self.view.dispatch(self.request)


class TestRoomAdminRequiredMixin(TestCase):
    """Test Room Admin Required Mixin"""

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="admin",
            last_name="user",
        )
        self.room = Room.objects.create(name="Test Room", admin=self.admin)
        self.other_user = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="member",
            last_name="user",
        )

        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = SessionBase()

        # Set room id in session
        self.request.session["room_id"] = self.room.id

        # Create a view instance with the RoomAdminRequiredMixin
        self.view = RoomAdminRequiredMixin()

    def test_user_is_admin(self):
        """Test user is admin"""

        # set admin as request user
        self.request.user = self.admin

        # Assert calling dispatch should call super dispatch
        with self.assertRaisesMessage(
            AttributeError, "'super' object has no attribute 'dispatch'"
        ):
            # Call the dispatch method with the request
            self.view.dispatch(self.request)

    def test_user_is_not_admin(self):
        """Test user is not admin"""

        # set other user as request user
        self.request.user = self.other_user

        # Call the dispatch method with the request
        response = self.view.dispatch(self.request)

        # Assert access should be denied with Forbidden status code
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TestRoomInvitationTokenMixin(TestCase):
    """Test Room Invitation Token Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.token = "test_token"

        self.admin = User.objects.create_user(
            email="admin@user.com",
            password="test-password",
            first_name="admin",
            last_name="user",
        )
        self.member = User.objects.create_user(
            email="member@user.com",
            password="test-password",
            first_name="admin",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.admin)
        self.token_payload = {"id": 1, "room": self.room, "email": self.member.email}

        # Create a view instance with the RoomInvitationTokenMixin
        self.view = RoomInvitationTokenMixin()

    @mock.patch(
        "accounts.mixins.RoomInvitationTokenMixin.check_room_invitation_token_valid"
    )
    def test_get_token_method_retrieve_token_from_get_request(
        self,
        mock_check_room_invitation_token_valid,
    ) -> None:
        """Test get token method retrieve token from get request"""

        # Set return value true
        mock_check_room_invitation_token_valid.return_value = True

        # Create request
        request = self.factory.get("/", data={"token": self.token})

        # Call get token method with request
        token = self.view.get_token(request)

        # Assert token value
        self.assertEqual(token, self.token)

        # Assert check_room_invitation_token_valid called once with expected args
        mock_check_room_invitation_token_valid.assert_called_once_with(
            request,
            self.token,
        )

    @mock.patch(
        "accounts.mixins.RoomInvitationTokenMixin.check_room_invitation_token_valid"
    )
    def test_get_token_method_retrieve_token_from_post_request(
        self,
        mock_check_room_invitation_token_valid,
    ) -> None:
        """Test get token method retrieve token from post request"""

        # Set return value true
        mock_check_room_invitation_token_valid.return_value = True

        # Create request
        request = self.factory.post("/", data={"token": self.token})

        # Call get token method with request
        token = self.view.get_token(request)

        # Assert token value
        self.assertEqual(token, self.token)

        # Assert check_room_invitation_token_valid called once with expected args
        mock_check_room_invitation_token_valid.assert_called_once_with(
            request,
            self.token,
        )

    def test_get_token_method_returns_404_not_found_if_token_missing(self) -> None:
        """Test get token method returns 404 not found if token missing"""

        # Create request
        request = self.factory.get("/")

        # Call get token method with request
        response = self.view.get_token(request)

        # Assert response is 404 not found
        self.assertIsInstance(response, HttpResponseNotFound)

    @mock.patch(
        "accounts.mixins.RoomInvitationTokenMixin.check_room_invitation_token_valid"
    )
    def test_get_token_method_400_bad_request_if_token_is_invalid(
        self,
        mock_check_room_invitation_token_valid,
    ) -> None:
        """Test get token method returns 400 bad request if token is invalid"""

        # Set return value true
        mock_check_room_invitation_token_valid.return_value = False

        # Create request
        request = self.factory.post("/", data={"token": self.token})

        # Call get token method with request
        response = self.view.get_token(request)

        # Assert response is 400 bad request
        self.assertIsInstance(response, HttpResponseBadRequest)

        # Assert check_room_invitation_token_valid called once with expected args
        mock_check_room_invitation_token_valid.assert_called_once_with(
            request,
            self.token,
        )

    @mock.patch("accounts.mixins.RoomInvitation.objects.unsigned_token")
    def test_check_room_invitation_token_valid_returns_false_if_token_invalid(
        self,
        mock_unsigned_token,
    ) -> None:
        """Test check room invitation token valid returns false if token invalid"""

        # Raise BadSignature
        mock_unsigned_token.side_effect = BadSignature()

        # Create request
        request = self.factory.post("/")

        # Call check room invitation token method with request and token
        token_validity = self.view.check_room_invitation_token_valid(
            request,
            self.token,
        )

        # Assert validity is false
        self.assertEqual(token_validity, False)

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(self.token)

    @mock.patch("accounts.mixins.RoomInvitation.objects.unsigned_token")
    def test_check_room_invitation_token_valid_returns_false_if_user_for_anonymous_user(
        self,
        mock_unsigned_token,
    ) -> None:
        """Test check room invitation token valid returns false for anonymous user"""

        # Set return value true
        mock_unsigned_token.return_value = self.token_payload

        # Create request
        request = self.factory.post("/")
        request.user = AnonymousUser()

        # Call check room invitation token method with request and token
        token_validity = self.view.check_room_invitation_token_valid(
            request,
            self.token,
        )

        # Assert validity is false
        self.assertEqual(token_validity, False)

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(self.token)

    @mock.patch("accounts.mixins.RoomInvitation.objects.unsigned_token")
    def test_check_room_invitation_token_valid_returns_false_if_user_email_mismatch(
        self,
        mock_unsigned_token,
    ) -> None:
        """Test check room invitation token valid returns false if user email mismatch"""

        # Set return value true
        mock_unsigned_token.return_value = self.token_payload

        # Create test user
        user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )

        # Create request
        request = self.factory.post("/")
        request.user = user

        # Call check room invitation token method with request and token
        token_validity = self.view.check_room_invitation_token_valid(
            request,
            self.token,
        )

        # Assert validity is false
        self.assertEqual(token_validity, False)

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(self.token)

    @mock.patch("accounts.mixins.RoomInvitation.objects.unsigned_token")
    def test_check_room_invitation_token_valid_returns_false_if_room_initiation_not_exists(
        self,
        mock_unsigned_token,
    ) -> None:
        """Test check room invitation token valid returns false if room initiation not exists"""

        # Set return value true
        mock_unsigned_token.return_value = self.token_payload

        # Create request
        request = self.factory.post("/")
        request.user = self.member

        # Call check room invitation token method with request and token
        token_validity = self.view.check_room_invitation_token_valid(
            request,
            self.token,
        )

        # Assert validity is false
        self.assertEqual(token_validity, False)

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(self.token)

    @mock.patch("accounts.mixins.RoomInvitation.objects.get")
    @mock.patch("accounts.mixins.RoomInvitation.objects.unsigned_token")
    def test_check_room_invitation_token_valid_returns_true_if_room_initiation_exists(
        self,
        mock_unsigned_token,
        mock_room_invitation_get,
    ) -> None:
        """Test check room invitation token valid returns true if room initiation exists"""

        # Set return value true
        mock_unsigned_token.return_value = self.token_payload

        # Create room invitation
        RoomInvitation.objects.create(room=self.room, email=self.member.email)

        # Create request
        request = self.factory.post("/")
        request.user = self.member

        # Call check room invitation token method with request and token
        token_validity = self.view.check_room_invitation_token_valid(
            request,
            self.token,
        )

        # Assert validity is true
        self.assertEqual(token_validity, True)

        # Assert unsigned_token called once with expected token
        mock_unsigned_token.assert_called_once_with(self.token)

        # Assert room invitation get with expected token payload id
        mock_room_invitation_get.assert_called_once_with(
            id=self.token_payload["id"],
            status=RoomInvitation.PENDING,
        )
