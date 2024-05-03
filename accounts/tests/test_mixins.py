from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy

from accounts.mixins import RoomAdminRequiredMixin, RoomSessionMixin
from accounts.models import Room

User = get_user_model()


class TestRoomRequiredMixin(TestCase):
    """Test Room Required Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")

        # Create a view instance with the RoomSessionMixin
        self.view = RoomSessionMixin()

    def test_redirect_to_room_selection(self) -> None:
        """Test redirect to room selection"""

        # Empty session
        self.request.session = {}

        # Call the dispatch method with the request
        response = self.view.dispatch(self.request)

        # Check that the response is a redirect to the room selection page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse_lazy("accounts:room_selection"))

    def test_not_redirect_to_room_selection(self) -> None:
        """Test not redirect to room selection"""

        # Set room id in session
        self.request.session = {"room_id": 1}

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
            email="admin@user.com", password="test-password"
        )
        self.room = Room.objects.create(name="Test Room", admin=self.admin)
        self.other_user = User.objects.create_user(
            email="member@user.com", password="test-password"
        )

        self.factory = RequestFactory()
        self.request = self.factory.get("/")

        # Set room id in session
        self.request.session = {"room_id": self.room.id}

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
