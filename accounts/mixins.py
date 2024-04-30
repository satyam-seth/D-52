from django.shortcuts import redirect
from django.urls import reverse_lazy


class RoomSessionMixin:
    """Mixin to check if the room id is present in the session."""

    def dispatch(self, request, *args, **kwargs):
        """If room id not present in session, redirect the user to the room selection page."""

        if "room_id" not in request.session:
            # Redirect to the room page
            # Preserve the original URL as the 'next' parameter
            next_url = request.get_full_path()
            redirect_url = f"{reverse_lazy('accounts:room_selection')}?next={next_url}"
            return redirect(redirect_url)

        return super().dispatch(request, *args, **kwargs)
