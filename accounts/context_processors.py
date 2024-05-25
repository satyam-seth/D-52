import logging

from django.http import HttpRequest

from accounts.models import Room
from accounts.types import RoomContextType

logger = logging.getLogger(__name__)


def room(request: HttpRequest) -> RoomContextType:
    """Returns room context"""

    room_id = request.session.get("room_id")

    room_count = 0
    if request.user.is_authenticated:
        room_count = Room.objects.filter(memberships__member=request.user).count()

    if room_id:
        try:
            room_instance = Room.objects.get(id=room_id)
            return {"room": room_instance, "room_count": room_count}
        except Room.DoesNotExist:
            logger.warning("Room with id %s does not exist.", room_id)

    return {"room": None, "room_count": room_count}
