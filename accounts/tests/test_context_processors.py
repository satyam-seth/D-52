from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from accounts.context_processors import room
from accounts.models import Room

User = get_user_model()


class TestRoomContextProcessor(TestCase):
    """Test Room Context Processor"""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="test@user.com",
            password="test-password",
            first_name="test",
            last_name="user",
        )
        self.room = Room.objects.create(name="test-room", admin=self.user)

    def test_work_with_valid_room_id(self) -> None:
        """Test work with valid room id"""

        # Simulate a request with a valid room_id in the session
        request = self.factory.get("/")
        request.user = self.user
        request.session = {"room_id": self.room.id}

        # Call room context processor
        context = room(request)

        # Assertions
        self.assertEqual(context["room"], self.room)
        self.assertEqual(context["room_count"], 1)

    def test_work_with_invalid_room_id(self) -> None:
        """Test work with invalid room id"""

        # Simulate a request with an invalid room_id in the session
        request = self.factory.get("/")
        request.user = self.user
        request.session = {"room_id": 9999}

        # Call room context processor
        context = room(request)

        # Assertions
        self.assertIsNone(context["room"])
        self.assertEqual(context["room_count"], 1)

    def test_work_with_no_room_id_and_anonymous_user(self) -> None:
        """Test work with no room id and anonymous user"""

        # Simulate a request without a room_id in the session
        request = self.factory.get("/")
        request.user = AnonymousUser()
        request.session = {}

        context = room(request)
        self.assertIsNone(context["room"])
        self.assertEqual(context["room_count"], 0)

    def test_work_with_no_room_id_and_authenticated_user(self) -> None:
        """Test work with no room id and authenticated user"""

        # Simulate a request without a room_id in the session
        request = self.factory.get("/")
        request.user = self.user
        request.session = {}

        context = room(request)
        self.assertIsNone(context["room"])
        self.assertEqual(context["room_count"], 1)
