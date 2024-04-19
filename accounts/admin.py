from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile, Room, RoomInvitation, RoomMembership

from .models import User


class ProfileInline(admin.StackedInline):
    """Stacked Inline for profile model"""

    model = Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = ("id", "email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    inlines = [ProfileInline]


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


@admin.register(RoomInvitation)
class RoomInvitationAdmin(admin.ModelAdmin):
    """Admin config for RoomInvitaion model"""

    list_display = ("id", "room", "email", "status")
