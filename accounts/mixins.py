from typing import Any, Optional

from django.http import HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from accounts.models import Room


class RoomBaseMixin:
    """Base mixin for room-related checks."""

    def get_room_id(self, request: HttpRequest) -> Optional[int]:
        """Get the room ID from the session."""

        return request.session.get("room_id")

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Common logic for dispatching."""

        room_id = self.get_room_id(request)
        if room_id is None:
            return self.handle_no_room(request)
        return self.handle_room_exists(request, room_id, *args, **kwargs)

    def handle_no_room(self, request: HttpRequest) -> HttpResponseRedirect:
        """Handle case where no room ID is present."""

        return redirect(reverse_lazy("accounts:room_selection"))

    def handle_room_exists(
        self, request: HttpRequest, room_id: int, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Handle case where room ID is present."""

        return super().dispatch(request, *args, **kwargs)  # type: ignore


class RoomRequiredMixin(RoomBaseMixin):
    """Mixin to check if the room id is present in the session."""


class RoomAdminRequiredMixin(RoomBaseMixin):
    """
    Mixin to check if the current user is the admin of
    the room corresponding to the session room id.
    """

    def handle_room_exists(
        self, request: HttpRequest, room_id: int, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Handle case where no room ID is present."""

        room = get_object_or_404(Room, pk=room_id)
        if room.admin == request.user:
            return super().handle_room_exists(request, room_id, *args, **kwargs)

        # Note: We can also check if the current user is a room admin.
        # In this case, we can add an appropriate message and
        # redirect the user to the room selection page,
        # where we may display only rooms created by the current user.
        # The user can then choose a room, and upon redirection,
        # see the initiation of the selected room.
        # else return HttpResponseForbidden

        return HttpResponseForbidden()
