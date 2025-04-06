from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from accounts.models import Room


class RoomInvitationTokenPayload(TypedDict):
    """Room invitation token payload"""

    id: int
    room: int
    email: str


class RoomContextType(TypedDict):
    """Room Context"""

    room: Optional["Room"]
    room_count: int
