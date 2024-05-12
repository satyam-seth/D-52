from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetCompleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, ListView, TemplateView, View

from accounts.forms import (
    LoginForm,
    ProfileUpdateForm,
    RoomCreateForm,
    RoomInvitationForm,
    SignUpForm,
)
from accounts.mixins import RoomAdminRequiredMixin, RoomInvitationTokenMixin
from accounts.models import Profile, Room, RoomInvitation, RoomMembership


# Create your views here.
class ProfileTemplateView(LoginRequiredMixin, TemplateView):
    """View to show user profile"""

    template_name = "accounts/profile.html"


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """View to show user profile"""

    form_class = ProfileUpdateForm
    template_name = "accounts/profile_update.html"
    success_message = "Profile Updated !!"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form: Any) -> HttpResponse:
        # Get the current user's profile
        profile = Profile.objects.get(user=self.request.user)

        # Update the profile with the form data
        profile.avatar = form.cleaned_data["avatar"]
        profile.cover_photo = form.cleaned_data["cover_photo"]
        profile.save()
        return super().form_valid(form)


class UserLoginView(SuccessMessageMixin, LoginView):
    """View to handle user login"""

    authentication_form = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    success_message = "Logged In Successfully !!"
    extra_context = {"login_active": "active"}


class UserLogoutView(LogoutView):
    """View to handle user logout"""

    next_page = "core:home"
    success_message = "Logged Out Successfully !!"

    def dispatch(self, request, *args: Any, **kwargs: Any) -> Any:
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "Logged Out Successfully !!")
        return response


class UserSignUpView(SuccessMessageMixin, CreateView):
    """View to handle user signup"""

    form_class = SignUpForm
    success_message = "Account Created Successfully !!"
    success_url = reverse_lazy("accounts:room")
    template_name = "accounts/signup.html"
    extra_context = {"signup_active": "active"}

    def form_valid(self, form: SignUpForm) -> HttpResponse:
        valid = super().form_valid(form)

        # Login the user
        login(self.request, self.object)
        return valid


class RoomSelectionView(LoginRequiredMixin, View):
    """Room selection view to store current room id in session"""

    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handle get request for room selection
        If the user is a member of only one room, redirect them to the home page
        with the selected room set in the session. If the user is a member of
        multiple rooms, display the room selection page.
        """

        # get room membership
        room_memberships = RoomMembership.objects.filter(member=request.user).order_by(
            "-created_on"
        )

        # If the user isn't a member of any group, redirect to the room page
        if room_memberships.count() == 0:
            messages.warning(
                request,
                "Please create or join a room before selecting one.",
            )
            return redirect(reverse_lazy("accounts:room"))

        # If the user is a member of only one room, set that room in the session
        # and if user is owner of room redirect to the room invitation page else home page
        if room_memberships.count() == 1:
            room = room_memberships.first().room
            messages.info(request, f"Welcome to the room '{room.name}'")
            request.session["room_id"] = room.pk

            # TODO: redirect user to room dashboard instead of home, if not owner of the room
            if room.admin == request.user:
                return redirect(reverse_lazy("accounts:room_invitation"))

            return redirect(reverse_lazy("core:home"))

        # If the user is a member of multiple rooms, let the user choose a room as the current room

        paginator = Paginator(room_memberships, per_page=10, orphans=5)
        page = request.GET.get("page")
        room_memberships_page = paginator.get_page(page)

        return render(
            request,
            "accounts/room_selection.html",
            {"room_memberships_page": room_memberships_page},
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Handles the post request for room selection. If a valid room ID is provided
        in the post data and the user is a member of that room, it saves the room ID in the session
        and redirects to the home page. If the room ID is missing or invalid,
        or if the user is not a member of the room,
        it redirects back to the room selection page with an appropriate message.
        """
        room_id = request.POST.get("roomId")

        # check room id present in post data
        if room_id is None:
            messages.warning(request, "Room ID is required")
            return redirect(reverse_lazy("accounts:room_selection"))

        # check room is exists
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            messages.warning(request, "Room does not exist")
            return redirect(reverse_lazy("accounts:room_selection"))

        # room membership is exists
        room_membership = RoomMembership.objects.filter(member=request.user, room=room)
        if room_membership.exists():
            messages.info(request, f"Welcome to the room '{room.name}'")
            request.session["room_id"] = room.pk
            # TODO: redirect to room dashboard page
            return redirect(reverse_lazy("core:home"))

        messages.warning(request, "You are not a member of requested Room")
        return redirect(reverse_lazy("accounts:room_selection"))


class RoomTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view is used to display the room template
    which contains the links to join or create a room
    """

    template_name = "accounts/room.html"


class RoomInvitationListView(LoginRequiredMixin, RoomAdminRequiredMixin, ListView):
    """View to render list room invitation"""

    model = RoomInvitation
    paginate_by = 10
    paginate_orphans = 5
    # TODO: in future add created_at field and update ordering to '-created_id'
    # Order by primary key in descending order
    ordering = ["-id"]
    context_object_name = "room_invitation_list"
    template_name = "accounts/room_invitation_list.html"
    extra_context = {"room_invitation_active": "active"}

    def get_queryset(self):
        room_id = self.request.session["room_id"]
        queryset = super().get_queryset().filter(room__id=room_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = RoomInvitationForm()
        return context


class RoomInviteView(LoginRequiredMixin, RoomAdminRequiredMixin, View):
    """View to handle room invite post requests"""

    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle POST requests for inviting users to a room"""

        form = RoomInvitationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            room_id = self.request.session["room_id"]
            room = get_object_or_404(Room, id=room_id)

            invitation_url = reverse_lazy("accounts:room_invitation_join")
            absolute_invitation_url = request.build_absolute_uri(invitation_url)

            try:
                RoomInvitation.objects.send_invitation(
                    room=room,
                    email=email,
                    absolute_invitation_url=absolute_invitation_url,
                )
                messages.success(
                    request,
                    f"Email: '{email}' is successfully invited to room '{room.name}'",
                )
            except IntegrityError:
                messages.warning(
                    request,
                    f"Email: '{email}' is already invited to room '{room.name}'",
                )
        else:
            # Display specific form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
        return redirect(reverse_lazy("accounts:room_invitation"))


# class RoomJoinView(LoginRequiredMixin, FormView):
#     """
#     This view is used to display and handle the room join form
#     """

#     form_class = RoomJoinForm
#     template_name = "accounts/room_join.html"
#     success_url = reverse_lazy("core:home")

#     def form_valid(self, form: RoomJoinForm) -> HttpResponse:
#         room_id = form.cleaned_data["room_id"]
#         room = Room.objects.get(id=room_id)
#         # TODO: also update invitation status
#         # add the user to the room
#         membership = RoomMembership(user=self.request.user, room=room)

#         try:
#             membership.save()
#             # TODO: Notify the group admin and members that a new user has joined the group
#             messages.success(
#                 self.request, f"You have joined the room '{room_id}' successfully !!"
#             )
#         except IntegrityError as e:
#             print(e)
#             messages.success(
#                 self.request,
#                 f"You have already joined the room '{room_id}'",
#             )
#         return super().form_valid(form)


class RoomInvitationJoinView(LoginRequiredMixin, RoomInvitationTokenMixin, View):
    """View to handle room invitation join requests"""

    http_method_names = ["get"]

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle get request for room invitation join"""

        token_or_response = self.get_token(request)

        if isinstance(token_or_response, HttpResponse):
            return token_or_response

        # TODO: pass room details in context
        return render(
            request,
            "accounts/room_invitation_join.html",
            {"token": token_or_response},
        )


class RoomInvitationAcceptView(LoginRequiredMixin, RoomInvitationTokenMixin, View):

    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:

        token_or_response = self.get_token(request)

        if isinstance(token_or_response, HttpResponse):
            return token_or_response

        RoomInvitation.objects.accept_invitation(
            current_user=request.user,
            token=token_or_response,
        )
        token_payload = RoomInvitation.objects.unsigned_token(token_or_response)
        room = Room.objects.get(id=token_payload["room"])
        messages.success(
            request,
            f"Room '{room.name}' invitation accepted successfully.",
        )
        return redirect(reverse_lazy("accounts:room_selection"))


class RoomInvitationRejectView(LoginRequiredMixin, RoomInvitationTokenMixin, View):

    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:

        token_or_response = self.get_token(request)

        if isinstance(token_or_response, HttpResponse):
            return token_or_response

        RoomInvitation.objects.reject_invitation(
            current_user=request.user,
            token=token_or_response,
        )
        token_payload = RoomInvitation.objects.unsigned_token(token_or_response)
        room = Room.objects.get(id=token_payload["room"])
        messages.info(
            request,
            f"Room '{room.name}' invitation rejected successfully.",
        )
        return redirect(reverse_lazy("core:home"))


class RoomInvitationCancelView(LoginRequiredMixin, RoomAdminRequiredMixin, View):

    http_method_names = ["post"]

    def post(self, request: HttpRequest) -> HttpResponse:

        invitation_id = request.POST.get("invitationId")

        if invitation_id is None:
            return HttpResponseNotFound()

        invitation = RoomInvitation.objects.get(id=invitation_id)

        try:
            invitation.cancel()
        except ValidationError:
            return HttpResponseBadRequest()

        messages.info(
            request,
            # pylint: disable=line-too-long
            f"Invitation to Room '{invitation.room.name}' has been canceled for email '{invitation.email}'.",
        )
        return redirect(reverse_lazy("accounts:room_invitation"))


class RoomCreateView(LoginRequiredMixin, CreateView):
    """
    This view is used to display and handle the room create form
    """

    form_class = RoomCreateForm
    template_name = "accounts/room_create.html"
    success_url = reverse_lazy("accounts:room_invitation")

    def form_valid(self, form: RoomCreateForm) -> HttpResponse:
        room = form.save(commit=False)
        # make current user as admin
        room.admin = self.request.user
        room.save()
        messages.success(self.request, f"Room '{room.name}' created successfully!")
        # Note: On saving, the admin user is automatically joined
        # via the Room model's post-save signal
        messages.success(
            self.request, f"You have joined the room '{room.name}' successfully !!"
        )
        return super().form_valid(form)


# TODO: Create custom template or redirect password done view to home
class MyPasswordResetCompleteView(PasswordResetCompleteView):
    """View to handle user password complete"""

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["login_url"] = "/login/"
        return context
