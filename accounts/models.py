from django.conf import settings
from django.db import models

# Create your models here.


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
        return f"{self.user.username}'s profile"


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
        return f"{self.room.name}-{self.user.username}"
