from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from accounts.models import Room


class RoomSessionMixin:
    """Mixin to check if the room id is present in the session."""

    def dispatch(self, request, *args, **kwargs):
        """If room id not present in session, redirect the user to the room selection page."""

        if "room_id" not in request.session:
            # Redirect to the room page
            return redirect(reverse_lazy("accounts:room_selection"))

        return super().dispatch(request, *args, **kwargs)


class RoomAdminRequiredMixin:
    """
    Mixin to check if the current user is the admin of
    the room corresponding to the session room id.
    """

    def dispatch(self, request, *args, **kwargs):
        """
        If current user is not admin of room corresponding
        to the session room id, return forbidden response.
        """

        room_id = request.session["room_id"]
        room = get_object_or_404(Room, pk=room_id)
        if room.admin == request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()
