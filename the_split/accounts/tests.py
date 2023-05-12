from accounts.models import Profile
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test Profile Model"""

    def setUp(self) -> None:
        self.user = User.objects.create(username="test-user", password="test-password")

    def test_profile_creation(self) -> None:
        """Test profile model for default values"""

        # get profile instance created by create_profile signal
        profile = Profile.objects.get(user=self.user)

        # assert field values
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.avatar.name, "profile_avatars/avatar.png")
        self.assertEqual(
            profile.cover_photo.name, "profile_cover_photos/cover_photo.jpg"
        )

        # assert string representation
        self.assertEqual(str(profile), self.user.username)
