from http import HTTPStatus

from django.test import RequestFactory, TestCase
from django.urls import reverse_lazy

from accounts.mixins import RoomRequiredMixin


class TestRoomRequiredMixin(TestCase):
    """Test Room Required Mixin"""

    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_redirect_to_room_selection(self) -> None:
        """Test redirect to room selection"""

        # Create a request object without the room ID in the session
        request = self.factory.get("/")
        # Empty session
        request.session = {}

        # Create a view instance with the RoomSessionMixin
        view = RoomRequiredMixin()

        # Call the dispatch method with the request
        response = view.dispatch(request)

        # Check that the response is a redirect to the room selection page
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse_lazy("accounts:room_selection"))

    def test_not_redirect_to_room_selection(self) -> None:
        """Test not redirect to room selection"""

        # Create a request object without the room ID in the session
        request = self.factory.get("/")
        # Set room id in session
        request.session = {"room_id": 1}

        # Create a view instance with the RoomSessionMixin
        view = RoomRequiredMixin()

        # Assert calling dispatch should call super dispatch
        with self.assertRaisesMessage(
            AttributeError, "'super' object has no attribute 'dispatch'"
        ):
            # Call the dispatch method with the request
            view.dispatch(request)
