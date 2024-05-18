from typing import Any

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Profile, Room, RoomInvitation, RoomMembership

User = get_user_model()


# https://docs.djangoproject.com/en/5.0/ref/signals/#post-save
@receiver(post_save, sender=User)
def create_profile(
    sender, instance, created: bool, **kwargs: Any  # pylint: disable=unused-argument
) -> None:
    """Signal receiver function for creating a user profile upon user creation"""

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(
    sender, instance, **kwargs: Any  # pylint: disable=unused-argument
) -> None:
    """Signal receiver function for saving the user profile upon user instance save"""

    instance.profile.save()


@receiver(post_save, sender=Room)
def create_room_membership_for_admin(
    sender, instance, created: bool, **kwargs: Any  # pylint: disable=unused-argument
) -> None:
    """Signal receiver function for creating a room membership for admin upon room creation"""

    if created:
        RoomMembership.objects.create(member=instance.admin, room=instance)


@receiver(post_save, sender=RoomInvitation)
def room_invitation_post_save(
    sender, instance, created: bool, **kwarg: Any  # pylint: disable=unused-argument
) -> None:
    """Signal to create relationship on room invitation accept"""

    # TODO: send invitation status change notification email

    if not created and instance.status == RoomInvitation.ACCEPTED:
        member = User.objects.get(email=instance.email)
        RoomMembership.objects.create(member=member, room=instance.room)
