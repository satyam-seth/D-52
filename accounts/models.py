from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """User model for authntication"""

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

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "room")

    def __str__(self) -> str:
        return f"{self.room.name}-{self.user}"


class RoomInvitation(models.Model):
    """Model to store invitations for a room"""

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
