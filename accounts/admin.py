from django.contrib import admin

from accounts.models import Profile, Room, RoomMembership

# Register your models here.


# TODO: register profile under user model as inline
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin configuration for the Profile model."""

    list_display = (
        "id",
        "user",
        "avatar",
        "cover_photo",
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Admin configuration for the Room model"""

    list_display = ("id", "name", "admin")


@admin.register(RoomMembership)
class RoomMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for the RoomMembership model"""

    list_display = ("id", "user", "room")
