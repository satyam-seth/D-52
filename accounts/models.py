from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import RoomInvitationManager, UserManager


class User(AbstractUser):
    """User model for authentication"""

    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()


# TODO: mark user first and last name as required fields
# for now we are showing username as name in templates if use name is not found
# also add birthday and other basic details in future
# we are may be notify other room member about birthday
class Profile(models.Model):
    """Model to store profile info for users"""

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, related_name="profile", on_delete=models.CASCADE
    )
    # TODO: resize and rename file
    avatar = models.ImageField(
        default="profile_avatars/avatar.png", upload_to="profile_avatars"
    )
    # TODO: resize and rename file
    cover_photo = models.ImageField(
        default="profile_cover_photos/cover_photo.jpg", upload_to="profile_cover_photos"
    )

    def __str__(self) -> str:
        return f"{self.user}'s profile"


class Room(models.Model):
    """Model to store room"""

    name = models.CharField(max_length=100)
    admin = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_rooms",
    )

    def __str__(self) -> str:
        return self.name


class RoomMembership(models.Model):
    """Model to store room membership"""

    member = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="memberships")
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("member", "room")

    def __str__(self) -> str:
        return f"{self.room.name}-{self.member}"


class RoomInvitation(models.Model):
    """Model to store invitations for a room"""

    class Meta:
        # Define unique constraint to ensure no duplicate pending
        # invitations for the same room and email
        unique_together = ["room", "email", "status"]

    objects = RoomInvitationManager()

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (CANCELED, "Canceled"),
    ]

    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"{self.email} - {self.room.name}"

    # TODO: use signal to send invitation status change notification email

    def accept(self) -> None:
        """Accept the invitation"""

        if self.status != self.PENDING:
            raise ValidationError(
                f"Unable to accept invitation with status '{self.status}'"
            )
        self.status = self.ACCEPTED
        self.save()

    def cancel(self) -> None:
        """Cancel the invitation"""

        if self.status != self.PENDING:
            raise ValidationError(
                f"Unable to cancel invitation with status '{self.status}'"
            )
        self.status = self.CANCELED
        self.save()

    def reject(self) -> None:
        """Reject the invitation"""

        if self.status != self.PENDING:
            raise ValidationError(
                f"Unable to reject invitation with status '{self.status}'"
            )
        self.status = self.REJECTED
        self.save()

    def save(self, *args, **kwargs):
        if self.room.memberships.filter(member__email=self.email).exists():
            raise ValidationError(
                f"The email '{self.email}' has already joined the room '{self.room.name}'"
            )
        super().save(*args, **kwargs)
