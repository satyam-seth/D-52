import logging
from typing import Dict, Optional

from django.http import HttpRequest

from accounts.models import Room

logger = logging.getLogger(__name__)


def room(request: HttpRequest) -> Dict[str, Optional[Room]]:
    """Returns room context"""

    room_id = request.session.get("room_id")

    if room_id:
        try:
            room_instance = Room.objects.get(id=room_id)
            return {"room": room_instance}
        except Room.DoesNotExist:
            logger.warning("Room with id %s does not exist.", room_id)

    return {"room": None}
