from typing import Any, Optional

from django.core.signing import BadSignature
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseRedirect,
)
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from accounts.models import Room, RoomInvitation, RoomMembership


# TODO: should extend login require mixin
class RoomBaseMixin:
    """Base mixin for room-related checks."""

    def get_room_id(self, request: HttpRequest) -> Optional[int]:
        """Get the room ID from the session."""

        return request.session.get("room_id")

    def get_room(self, request: HttpRequest) -> Room:
        """Retrieves the room instance"""

        room_id = self.get_room_id(request)
        return get_object_or_404(Room, id=room_id)

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

    def handle_room_exists(
        self, request: HttpRequest, room_id: int, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Handle case where no room ID is present"""

        is_member = RoomMembership.objects.filter(
            room__id=room_id,
            member=request.user,  # type: ignore
        ).exists()

        if is_member:
            return super().handle_room_exists(request, room_id, *args, **kwargs)

        return redirect(reverse_lazy("accounts:room_selection"))


class RoomAdminRequiredMixin(RoomBaseMixin):
    """
    Mixin to check if the current user is the admin of
    the room corresponding to the session room id.
    """

    def handle_room_exists(
        self, request: HttpRequest, room_id: int, *args: Any, **kwargs: Any
    ) -> HttpResponseBase:
        """Handle case where room ID is present."""

        room = self.get_room(request)
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


class RoomInvitationTokenMixin:
    """Mixin to get and check room invitation token validation"""

    def check_room_invitation_token_valid(
        self, request: HttpRequest, token: str
    ) -> bool:
        """Check room invitation token valid"""

        try:
            token_payload = RoomInvitation.objects.unsigned_token(token)
        except BadSignature:
            return False

        # return false if user is not logged-in
        # or logged-in user email is not equal to token payload email
        if request.user.is_anonymous or request.user.email != token_payload["email"]:
            return False

        try:
            RoomInvitation.objects.get(
                id=token_payload["id"],
                status=RoomInvitation.PENDING,
            )
            return True

        except RoomInvitation.DoesNotExist:
            return False

    def get_token(self, request: HttpRequest) -> HttpResponse | str:
        """To get room invitation token from request"""

        token = None
        if request.method == "POST":
            token = request.POST.get("token")
        else:
            token = request.GET.get("token")

        # if token missing return 404
        if token is None:
            return HttpResponseNotFound()

        # check token is valid or not
        if self.check_room_invitation_token_valid(request, token) is False:
            return HttpResponseBadRequest()

        return token
