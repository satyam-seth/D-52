from typing import TypedDict


class RoomInvitationTokenPayload(TypedDict):
    """Room invitation token payload"""

    id: int
    room: int
    email: str
