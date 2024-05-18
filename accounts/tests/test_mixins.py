from http import HTTPStatus
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import SessionBase
from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy

from accounts.mixins import (
    RoomAdminRequiredMixin,
    RoomBaseMixin,
    RoomInvitationTokenMixin,
    RoomRequiredMixin,
)
from accounts.models import Room

User = get_user_model()


class TestRoomRoomBaseMixin(TestCase):
    """Test Room Required Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = SessionBase()
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


class TestRoomRequiredMixin(TestCase):
    """Test Room Required Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = SessionBase()

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

        # Set room id in session
        self.request.session["room_id"] = 1

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

        test_token = "test_token"

        # Create request
        request = self.factory.get("/", data={"token": test_token})

        # Call get token method with request
        token = self.view.get_token(request)

        # Assert token value
        self.assertEqual(token, test_token)

        # Assert check_room_invitation_token_valid called once with expected args
        mock_check_room_invitation_token_valid.assert_called_once_with(
            request,
            test_token,
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

        test_token = "test_token"

        # Create request
        request = self.factory.post("/", data={"token": test_token})

        # Call get token method with request
        token = self.view.get_token(request)

        # Assert token value
        self.assertEqual(token, test_token)

        # Assert check_room_invitation_token_valid called once with expected args
        mock_check_room_invitation_token_valid.assert_called_once_with(
            request,
            test_token,
        )
