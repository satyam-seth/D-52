from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Model manager for User model"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


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
