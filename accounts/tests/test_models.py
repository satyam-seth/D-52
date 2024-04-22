from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Profile, Room, RoomInvitation, RoomMembership

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test Profile Model"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@user.com", password="test-password"
        )

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
        self.assertEqual(str(profile), f"{self.user}'s profile")


class RoomModelTest(TestCase):
    """Test Room Model"""

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email="test@user.com", password="test-password"
        )

    def test_room_creation(self) -> None:
        """Test room model for default values"""

        # create room instance
        room = Room.objects.create(name="test-room", admin=self.admin)

        # assert field values
        self.assertEqual(room.admin, self.admin)
        self.assertEqual(room.name, "test-room")

        # assert string representation
        self.assertEqual(str(room), room.name)


class RoomInvitationModelTest(TestCase):
    """Test RoomInvitation Model"""

    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            email="admin@user.com", password="test-password"
        )
        self.room = Room.objects.create(name="test-room", admin=self.admin)
        self.member_email = "member@user.com"

    def test_room_invitation_creation(self) -> None:
        """Test room invitations model for default values"""

        # create room invitation instance
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email
        )
        # assert field values
        self.assertEqual(invitation.room, self.room)
        self.assertEqual(invitation.email, self.member_email)

        # assert string representation
        self.assertEqual(str(invitation), f"{self.member_email} - {self.room.name}")

    def test_accept_pending_invitation(self) -> None:
        """Test accepting a pending room invitation"""

        # create room invitation instance
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email
        )

        # call the accept method on the room invitation
        invitation.accept()

        # check that the status of the invitation is updated to 'accepted'
        self.assertEqual(invitation.status, RoomInvitation.ACCEPTED)

    def test_accept_already_accepted_invitation(self) -> None:
        """Test attempting to accept an already accepted room invitation"""

        # create room invitation with status 'accepted'
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email, status=RoomInvitation.ACCEPTED
        )

        # call the accept method on the room invitation
        with self.assertRaisesMessage(
            ValidationError,
            f"Unable to accept invitation with status '{invitation.status}'",
        ):
            invitation.accept()

    def test_cancel_pending_invitation(self) -> None:
        """Test canceling a pending room invitation"""

        # create room invitation instance
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email
        )

        # call the cancel method on the room invitation
        invitation.cancel()

        # check that the status of the invitation is updated to 'canceled'
        self.assertEqual(invitation.status, RoomInvitation.CANCELED)

    def test_cancel_already_accepted_invitation(self) -> None:
        """Test attempting to cancel an already accepted room invitation"""

        # create room invitation with status 'accepted'
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email, status=RoomInvitation.ACCEPTED
        )

        # call the cancel method on the room invitation
        with self.assertRaisesMessage(
            ValidationError,
            f"Unable to cancel invitation with status '{invitation.status}'",
        ):
            invitation.cancel()

    def test_reject_pending_invitation(self) -> None:
        """Test rejecting a pending room invitation"""

        # create room invitation instance
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email
        )

        # call the reject method on the room invitation
        invitation.reject()

        # check that the status of the invitation is updated to 'rejected'
        self.assertEqual(invitation.status, RoomInvitation.REJECTED)

    def test_reject_already_accepted_invitation(self):
        """Test attempting to reject an already accepted room invitation"""

        # create room invitation with status 'accepted'
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email, status=RoomInvitation.ACCEPTED
        )

        # call the reject method on the room invitation
        with self.assertRaisesMessage(
            ValidationError,
            f"Unable to reject invitation with status '{invitation.status}'",
        ):
            invitation.reject()

    def test_unable_to_create_invitation_for_an_existing_room_member(self) -> None:
        """Test unable to create room invitation for an existing room member"""

        # create user for room member
        member = User.objects.create_user(
            email=self.member_email, password="test-password"
        )
        RoomMembership.objects.create(member=member, room=self.room)
        with self.assertRaisesMessage(
            ValidationError,
            f"The email '{self.member_email}' has already joined the room '{self.room.name}'",
        ):
            RoomInvitation.objects.send_invitation(
                room=self.room, email=self.member_email
            )

    @patch.object(RoomInvitation.objects, "create")
    @patch.object(RoomInvitation.objects, "_generate_signed_token")
    def test_send_invitation(self, mock_generate_signed_token, mock_create) -> None:
        """Test sending an invitation to join a room"""

        # set up mock objects and return values
        mock_invitation = RoomInvitation(id=1, room=self.room, email=self.member_email)
        mock_create.return_value = mock_invitation
        token = "mock_token"
        mock_generate_signed_token.return_value = token

        # call send_invitation
        invitation = RoomInvitation.objects.send_invitation(
            room=self.room, email=self.member_email
        )

        # assertions
        self.assertEqual(invitation, mock_invitation)
        mock_create.assert_called_once_with(room=self.room, email=self.member_email)
        mock_generate_signed_token.assert_called_once_with(invitation=mock_invitation)

    @patch.object(RoomInvitation, "accept")
    @patch.object(RoomInvitation.objects, "_unsigned_token")
    def test_accept_invitation(self, mock_unsigned_token, mock_accept) -> None:
        """Test accepting an invitation"""
        # set up mock objects and return values
        invitation = RoomInvitation.objects.create(
            room=self.room, email=self.member_email
        )
        token = "mock_token"
        mock_unsigned_token.return_value = {
            "id": invitation.id,
            "room": self.room.id,
            "email": self.member_email,
        }

        member = User.objects.create_user(
            email=self.member_email, password="test-password"
        )

        # call accept_invitation
        RoomInvitation.objects.accept_invitation(member, token)

        # assertions
        mock_unsigned_token.assert_called_once_with(token=token)
        mock_accept.assert_called_once()
